{{
    config(
        materialized='table'
    )
}}

WITH trip_durations AS(
    SELECT 
        pickup_zone, 
        dropoff_zone,
        TIMESTAMP_DIFF(dropoff_datetime, pickup_datetime, SECOND) AS trip_duration,
        PERCENTILE_CONT(TIMESTAMP_DIFF(dropoff_datetime, pickup_datetime, SECOND), 0.9) OVER (
            PARTITION BY pickup_year, pickup_month, pickup_zone, dropoff_zone
        ) AS trip_duration_p90
        from {{ ref('dim_fhv_trips') }}
    WHERE pickup_zone IN ('Newark Airport', 'SoHo', 'Yorkville East')
        AND pickup_year = 2019
        AND pickup_month = 11

),
ranked_trips AS(
    SELECT *,
        DENSE_RANK() OVER (PARTITION BY pickup_zone ORDER BY trip_duration_p90 DESC) AS p90_rank
    FROM trip_durations
)
SELECT DISTINCT pickup_zone, dropoff_zone, trip_duration_p90
FROM ranked_trips
WHERE p90_rank = 2