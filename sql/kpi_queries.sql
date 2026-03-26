-- Revenue, cost, and profitability by region and product category
SELECT
    region,
    product_category,
    COUNT(*) AS orders,
    SUM(units) AS units_sold,
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    ROUND(SUM(product_cost + operating_cost), 2) AS total_cost,
    ROUND(SUM(gross_profit), 2) AS gross_profit,
    ROUND(SUM(gross_profit) * 1.0 / NULLIF(SUM(net_revenue), 0), 4) AS margin_pct
FROM fact_order_kpis
GROUP BY region, product_category
ORDER BY gross_profit DESC;

-- Monthly commercial and logistics trendline for dashboarding
SELECT
    year_month,
    region,
    product_category,
    COUNT(*) AS orders,
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    ROUND(SUM(gross_profit), 2) AS gross_profit,
    ROUND(AVG(actual_delivery_days), 2) AS avg_delivery_days,
    ROUND(AVG(on_time_flag), 4) AS on_time_rate,
    ROUND(AVG(return_flag), 4) AS return_rate
FROM fact_order_kpis
GROUP BY year_month, region, product_category
ORDER BY year_month, region, product_category;

-- Operational bottlenecks: slower fulfillment, backorders, and missed delivery SLAs
SELECT
    region,
    product_category,
    ROUND(AVG(processing_days), 2) AS avg_processing_days,
    ROUND(AVG(actual_delivery_days), 2) AS avg_delivery_days,
    ROUND(AVG(delay_days), 2) AS avg_delay_days,
    ROUND(AVG(backorder_flag), 4) AS backorder_rate,
    ROUND(AVG(on_time_flag), 4) AS on_time_rate
FROM fact_order_kpis
GROUP BY region, product_category
ORDER BY avg_delay_days DESC, backorder_rate DESC;

-- Underperforming segments compared with portfolio-wide benchmarks
WITH portfolio_benchmarks AS (
    SELECT
        SUM(gross_profit) * 1.0 / NULLIF(SUM(net_revenue), 0) AS margin_benchmark,
        AVG(on_time_flag) AS on_time_benchmark,
        AVG(return_flag) AS return_benchmark,
        AVG(backorder_flag) AS backorder_benchmark,
        AVG(actual_delivery_days) AS delivery_benchmark
    FROM fact_order_kpis
)
SELECT
    s.region,
    s.product_category,
    s.net_revenue,
    s.gross_profit,
    s.margin_pct,
    s.avg_delivery_days,
    s.on_time_rate,
    s.return_rate,
    s.backorder_rate
FROM segment_scorecard s
CROSS JOIN portfolio_benchmarks b
WHERE s.margin_pct < b.margin_benchmark
   OR s.on_time_rate < b.on_time_benchmark
   OR s.return_rate > b.return_benchmark
   OR s.backorder_rate > b.backorder_benchmark
   OR s.avg_delivery_days > b.delivery_benchmark
ORDER BY s.margin_pct ASC, s.on_time_rate ASC;

-- Best-performing segments for benchmark comparison
SELECT
    region,
    product_category,
    net_revenue,
    gross_profit,
    margin_pct,
    on_time_rate,
    return_rate
FROM segment_scorecard
ORDER BY gross_profit DESC
LIMIT 5;
