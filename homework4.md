## Module 4 Homework

### Question 1: Understanding dbt model resolution

Provided you've got the following sources.yaml
```yaml
version: 2

sources:
  - name: raw_nyc_tripdata
    database: "{{ env_var('DBT_BIGQUERY_PROJECT', 'dtc_zoomcamp_2025') }}"
    schema:   "{{ env_var('DBT_BIGQUERY_SOURCE_DATASET', 'raw_nyc_tripdata') }}"
    tables:
      - name: ext_green_taxi
      - name: ext_yellow_taxi
```

with the following env variables setup where `dbt` runs:
```shell
export DBT_BIGQUERY_PROJECT=myproject
export DBT_BIGQUERY_DATASET=my_nyc_tripdata
```

What does this .sql model compile to?
```sql
select * 
from {{ source('raw_nyc_tripdata', 'ext_green_taxi' ) }}
```

The correct answer is:

```sql
select * from myproject.raw_nyc_tripdata.ext_green_taxi
```

Here's why:

1. In the sources.yaml file, the database and schema are defined using env_var functions:
   - database: `"{{ env_var('DBT_BIGQUERY_PROJECT', 'dtc_zoomcamp_2025') }}"`
   - schema: `"{{ env_var('DBT_BIGQUERY_SOURCE_DATASET', 'raw_nyc_tripdata') }}"`

2. Since the environment variables are set:
   - `DBT_BIGQUERY_PROJECT=myproject`
   - `DBT_BIGQUERY_DATASET=my_nyc_tripdata`

3. The database will resolve to 'myproject' (from the environment variable) instead of the default 'dtc_zoomcamp_2025'

4. The schema will resolve to 'raw_nyc_tripdata' (the default value, since there's no environment variable set for DBT_BIGQUERY_SOURCE_DATASET)

5. The table name 'ext_green_taxi' remains unchanged

Therefore, when dbt compiles the source reference:
`{{ source('raw_nyc_tripdata', 'ext_green_taxi' ) }}`

It will resolve to:
**`myproject.raw_nyc_tripdata.ext_green_taxi`**

### Question 2: dbt Variables & Dynamic Models

Say you have to modify the following dbt_model (`fct_recent_taxi_trips.sql`) to enable Analytics Engineers to dynamically control the date range. 

- In development, you want to process only **the last 7 days of trips**
- In production, you need to process **the last 30 days** for analytics

```sql
select *
from {{ ref('fact_taxi_trips') }}
where pickup_datetime >= CURRENT_DATE - INTERVAL '30' DAY
```

What would you change to accomplish that in a such way that command line arguments takes precedence over ENV_VARs, which takes precedence over DEFAULT value?

The correct answer is:
```sql
Update the WHERE clause to pickup_datetime >= CURRENT_DATE - INTERVAL '{{ var("days_back", env_var("DAYS_BACK", "30")) }}' DAY
```

This is the correct solution because it implements the desired precedence order:
1. Command line arguments (via `var()`)
2. Environment variables (via `env_var()`)
3. Default value ("30")

Here's how it works:

1. First, it looks for a variable `days_back` that could be set via command line (--vars 'days_back: 7')
2. If that's not found, it evaluates `env_var("DAYS_BACK", "30")`
   - This looks for an environment variable DAYS_BACK
   - If DAYS_BACK isn't set, it uses "30" as the final fallback

So the precedence works like this:
- Command line: `dbt run --vars 'days_back: 7'` (highest priority)
- If not found, checks environment: `export DAYS_BACK=15`
- If neither is found, uses default: "30" (lowest priority)


### Question 3: dbt Data Lineage and Execution

Considering the data lineage in question **and** that taxi_zone_lookup is the **only** materialization build (from a .csv seed file):

Select the option that does **NOT** apply for materializing `fct_taxi_monthly_zone_revenue`:

The correct answer is: **`dbt run --select models/staging/+`**

This is because while it runs the staging models and their downstream dependencies, it doesn't include the seed file (taxi_zone_lookup) which is needed for dim_zone_lookup, which in turn is needed for the final materialization.



### Question 4: dbt Macros and Jinja

Consider you're dealing with sensitive data (e.g.: [PII](https://en.wikipedia.org/wiki/Personal_data)), that is **only available to your team and very selected few individuals**, in the `raw layer` of your DWH (e.g: a specific BigQuery dataset or PostgreSQL schema), 

 - Among other things, you decide to obfuscate/masquerade that data through your staging models, and make it available in a different schema (a `staging layer`) for other Data/Analytics Engineers to explore

- And **optionally**, yet  another layer (`service layer`), where you'll build your dimension (`dim_`) and fact (`fct_`) tables (assuming the [Star Schema dimensional modeling](https://www.databricks.com/glossary/star-schema)) for Dashboarding and for Tech Product Owners/Managers

You decide to make a macro to wrap a logic around it:

```sql
{% macro resolve_schema_for(model_type) -%}

    {%- set target_env_var = 'DBT_BIGQUERY_TARGET_DATASET'  -%}
    {%- set stging_env_var = 'DBT_BIGQUERY_STAGING_DATASET' -%}

    {%- if model_type == 'core' -%} {{- env_var(target_env_var) -}}
    {%- else -%}                    {{- env_var(stging_env_var, env_var(target_env_var)) -}}
    {%- endif -%}

{%- endmacro %}
```

And use on your staging, dim_ and fact_ models as:
```sql
{{ config(
    schema=resolve_schema_for('core'), 
) }}
```

That all being said, regarding macro above, **select all statements that are true to the models using it**.

The correct statements are:

1. **"Setting a value for `DBT_BIGQUERY_TARGET_DATASET` env var is mandatory, or it'll fail to compile"**
2. **"When using `core`, it materializes in the dataset defined in `DBT_BIGQUERY_TARGET_DATASET`"**
3. **When using `staging`, it materializes in the dataset defined in `DBT_BIGQUERY_STAGING_DATASET`, or defaults to `DBT_BIGQUERY_TARGET_DATASET`**

Let's analyze why:

1. `DBT_BIGQUERY_TARGET_DATASET` is mandatory because:
   - For 'core' models, it's used directly without a fallback value
   - For other models, it's used as the fallback value for `DBT_BIGQUERY_STAGING_DATASET`
   - If it's not set, the macro will fail as there's no default value provided

2. `DBT_BIGQUERY_STAGING_DATASET` is NOT mandatory because:
   - It has a fallback to `DBT_BIGQUERY_TARGET_DATASET` in the macro
   - `env_var(stging_env_var, env_var(target_env_var))`

3. For 'core' models:
   - The macro returns `env_var(target_env_var)`
   - This directly uses the value from `DBT_BIGQUERY_TARGET_DATASET`

4. For any non-'core' models (including both 'stg' and 'staging'):
   - The macro uses the else clause
   - It tries to use `DBT_BIGQUERY_STAGING_DATASET` first
   - If that's not set, it falls back to `DBT_BIGQUERY_TARGET_DATASET`

Note: The statement about "staging" is redundant with the one about "stg" as the macro treats all non-'core' values the same way in the else clause.

### Question 5: Taxi Quarterly Revenue Growth

1. Create a new model `fct_taxi_trips_quarterly_revenue.sql`
2. Compute the Quarterly Revenues for each year for based on `total_amount`
3. Compute the Quarterly YoY (Year-over-Year) revenue growth 
  * e.g.: In 2020/Q1, Green Taxi had -12.34% revenue growth compared to 2019/Q1
  * e.g.: In 2020/Q4, Yellow Taxi had +34.56% revenue growth compared to 2019/Q4

Considering the YoY Growth in 2020, which were the yearly quarters with the best (or less worse) and worst results for green, and yellow.

In order to answer this question we need to modify `fact_trips.sql` model and create new one `fct_taxi_trips_quarterly_revenue.sql`.

```sql
{{
    config(
        materialized='table'
    )
}}

with green_tripdata as (
    select *,
    'Green' as service_type
    from {{ ref('stg_green_tripdata') }}
),
yellow_tripdata as (
    select *,
    'Yellow' as service_type
    from {{ ref('stg_yellow_tripdata') }}
),
trips_unioned as (
    select * from green_tripdata
    union all
    select * from yellow_tripdata
),
dim_zones as (
    select * from {{ ref('dim_zones') }}
    where borough != 'Unknown'
),
trips AS (
    SELECT trips_unioned.tripid, 
    trips_unioned.vendorid, 
    trips_unioned.service_type,
    trips_unioned.ratecodeid, 
    trips_unioned.pickup_locationid, 
    pickup_zone.borough as pickup_borough, 
    pickup_zone.zone as pickup_zone, 
    trips_unioned.dropoff_locationid,
    dropoff_zone.borough as dropoff_borough, 
    dropoff_zone.zone as dropoff_zone,  
    trips_unioned.pickup_datetime, 
    trips_unioned.dropoff_datetime, 
    trips_unioned.store_and_fwd_flag, 
    trips_unioned.passenger_count, 
    trips_unioned.trip_distance, 
    trips_unioned.trip_type, 
    trips_unioned.fare_amount, 
    trips_unioned.extra, 
    trips_unioned.mta_tax, 
    trips_unioned.tip_amount, 
    trips_unioned.tolls_amount, 
    trips_unioned.ehail_fee, 
    trips_unioned.improvement_surcharge, 
    trips_unioned.total_amount, 
    trips_unioned.payment_type, 
    trips_unioned.payment_type_description,
    EXTRACT(YEAR FROM trips_unioned.pickup_datetime) AS pickup_year,
    EXTRACT(MONTH FROM trips_unioned.pickup_datetime) AS pickup_month,
    EXTRACT(QUARTER FROM trips_unioned.pickup_datetime) AS pickup_quarter
from trips_unioned
inner join dim_zones as pickup_zone
on trips_unioned.pickup_locationid = pickup_zone.locationid
inner join dim_zones as dropoff_zone
on trips_unioned.dropoff_locationid = dropoff_zone.locationid
)

SELECT trips.*,
    CONCAT(CAST(pickup_year AS STRING), '/', CAST(pickup_quarter AS STRING)) AS year_quarter
    from trips
```


```sql
{{
    config(
        materialized='table'
    )
}}

WITH quarterly_revenue AS (
    SELECT pickup_year,
            pickup_quarter,
            service_type,
            SUM(total_amount) as quarterly_revenue
    FROM {{ ref('fact_trips') }}
    WHERE pickup_year IN (2019,2020)
    GROUP BY pickup_year,pickup_quarter,service_type
)

SELECT 
    qr.pickup_quarter,
    qr.service_type,
    qr.quarterly_revenue,
    qr_prev_year.quarterly_revenue AS previous_year_revenue,
    (qr.quarterly_revenue / qr_prev_year.quarterly_revenue) * 100 AS YOY_Growth
FROM quarterly_revenue qr
INNER JOIN quarterly_revenue qr_prev_year
    ON qr.service_type = qr_prev_year.service_type
    AND qr.pickup_quarter = qr_prev_year.pickup_quarter
    AND qr.pickup_year = qr_prev_year.pickup_year + 1
ORDER BY YOY_Growth DESC
```

The correct asnwer is **green: {best: 2020/Q1, worst: 2020/Q2}, yellow: {best: 2020/Q1, worst: 2020/Q2}**


### Question 6: P97/P95/P90 Taxi Monthly Fare

1. Create a new model `fct_taxi_trips_monthly_fare_p95.sql`
2. Filter out invalid entries (`fare_amount > 0`, `trip_distance > 0`, and `payment_type_description in ('Cash', 'Credit Card')`)
3. Compute the **continous percentile** of `fare_amount` partitioning by service_type, year and and month

Now, what are the values of `p97`, `p95`, `p90` for Green Taxi and Yellow Taxi, in April 2020?

- green: {p97: 55.0, p95: 45.0, p90: 26.5}, yellow: {p97: 52.0, p95: 37.0, p90: 25.5}
- green: {p97: 55.0, p95: 45.0, p90: 26.5}, yellow: {p97: 31.5, p95: 25.5, p90: 19.0}
- green: {p97: 40.0, p95: 33.0, p90: 24.5}, yellow: {p97: 52.0, p95: 37.0, p90: 25.5}
- green: {p97: 40.0, p95: 33.0, p90: 24.5}, yellow: {p97: 31.5, p95: 25.5, p90: 19.0}
- green: {p97: 55.0, p95: 45.0, p90: 26.5}, yellow: {p97: 52.0, p95: 25.5, p90: 19.0}


### Question 7: Top #Nth longest P90 travel time Location for FHV

Prerequisites:
* Create a staging model for FHV Data (2019), and **DO NOT** add a deduplication step, just filter out the entries where `where dispatching_base_num is not null`
* Create a core model for FHV Data (`dim_fhv_trips.sql`) joining with `dim_zones`. Similar to what has been done [here](../../../04-analytics-engineering/taxi_rides_ny/models/core/fact_trips.sql)
* Add some new dimensions `year` (e.g.: 2019) and `month` (e.g.: 1, 2, ..., 12), based on `pickup_datetime`, to the core model to facilitate filtering for your queries

Now...
1. Create a new model `fct_fhv_monthly_zone_traveltime_p90.sql`
2. For each record in `dim_fhv_trips.sql`, compute the [timestamp_diff](https://cloud.google.com/bigquery/docs/reference/standard-sql/timestamp_functions#timestamp_diff) in seconds between dropoff_datetime and pickup_datetime - we'll call it `trip_duration` for this exercise
3. Compute the **continous** `p90` of `trip_duration` partitioning by year, month, pickup_location_id, and dropoff_location_id

For the Trips that **respectively** started from `Newark Airport`, `SoHo`, and `Yorkville East`, in November 2019, what are **dropoff_zones** with the 2nd longest p90 trip_duration ?

- LaGuardia Airport, Chinatown, Garment District
- LaGuardia Airport, Park Slope, Clinton East
- LaGuardia Airport, Saint Albans, Howard Beach
- LaGuardia Airport, Rosedale, Bath Beach
- LaGuardia Airport, Yorkville East, Greenpoint