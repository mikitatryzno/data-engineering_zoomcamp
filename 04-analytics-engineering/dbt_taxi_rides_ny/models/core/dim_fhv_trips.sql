{{
    config(
        materialized='table'
    )
}}


WITH
dim_zones as (
    select * from {{ ref('dim_zones') }}
    where borough != 'Unknown'
)

SELECT dispatching_base_num,
    pickup_datetime,
    dropoff_datetime,
    pulocationid,
    pickup_zone.borough as pickup_borough, 
    pickup_zone.zone as pickup_zone, 
    dolocationid,
    dropoff_zone.borough as dropoff_borough, 
    dropoff_zone.zone as dropoff_zone,  
    sr_flag,
    affiliated_base_number,
    EXTRACT(YEAR FROM pickup_datetime) AS pickup_year,
    EXTRACT(MONTH FROM pickup_datetime) AS pickup_month
from {{ ref('stg_fhv_tripdata') }} as fhv
inner join dim_zones as pickup_zone
on fhv.pulocationid = pickup_zone.locationid
inner join dim_zones as dropoff_zone
on fhv.dolocationid = dropoff_zone.locationid