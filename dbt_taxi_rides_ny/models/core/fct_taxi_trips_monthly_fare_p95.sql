{{
    config(
        materialized='table'
    )
}}

WITH filtered_trips AS (
    SELECT 
        pickup_year,
        pickup_month,
        service_type,
        fare_amount
    FROM {{ ref('fact_trips') }}
    WHERE 
        fare_amount > 0 
        AND trip_distance > 0 
        AND LOWER(payment_type_description) IN ('cash', 'credit card')
        AND pickup_year = 2020
        AND pickup_month = 4
),

percentiles AS (
    SELECT DISTINCT
        pickup_year,
        pickup_month,
        service_type,
        PERCENTILE_CONT(fare_amount, 0.97) OVER (
            PARTITION BY service_type, pickup_year, pickup_month
        ) AS p97,
        PERCENTILE_CONT(fare_amount, 0.95) OVER (
            PARTITION BY service_type, pickup_year, pickup_month
        ) AS p95,
        PERCENTILE_CONT(fare_amount, 0.90) OVER (
            PARTITION BY service_type, pickup_year, pickup_month
        ) AS p90
    FROM filtered_trips
)

SELECT * FROM percentiles
