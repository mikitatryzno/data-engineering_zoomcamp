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