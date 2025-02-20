{{ config(materialized="view") }}

with
    tripdata as (
        select *, row_number() over (partition by pulocationid, pickup_datetime) as rn
        from {{ source("staging", "fhv_taxi") }}
    )

select
    {{ dbt_utils.generate_surrogate_key(["pulocationid", "pickup_datetime"]) }}
    as tripid,
    {{ dbt.safe_cast("dispatching_base_num", api.Column.translate_type("integer")) }}
    as dispatching_base_num,
    cast(pickup_datetime as timestamp) as pickup_datetime,
    cast(dropoff_datetime as timestamp) as dropoff_datetime,
    {{ dbt.safe_cast("pulocationid", api.Column.translate_type("integer")) }}
    as pickup_locationid,
    {{ dbt.safe_cast("dolocationid", api.Column.translate_type("integer")) }}
    as dropoff_locationid,
    sr_flag,
    affiliated_base_number

from tripdata
--where rn = 1

-- dbt build --select <model.sql> --vars '{'is_test_run: false}'
{% if var("is_test_run", default=true) %} limit 100 {% endif %}