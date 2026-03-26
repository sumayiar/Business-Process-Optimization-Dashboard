SELECT
    region,
    product_category,
    COUNT(*) AS orders,
    SUM(units) AS units_sold,
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    ROUND(SUM(gross_profit), 2) AS gross_profit,
    ROUND(SUM(gross_profit) * 1.0 / NULLIF(SUM(net_revenue), 0), 4) AS margin_pct,
    ROUND(AVG(actual_delivery_days), 2) AS avg_delivery_days,
    ROUND(AVG(on_time_flag), 4) AS on_time_rate,
    ROUND(AVG(return_flag), 4) AS return_rate,
    ROUND(AVG(backorder_flag), 4) AS backorder_rate,
    ROUND(AVG(discount_pct), 4) AS avg_discount_pct,
    RANK() OVER (ORDER BY SUM(gross_profit) DESC) AS profitability_rank
FROM fact_order_kpis
GROUP BY region, product_category
ORDER BY gross_profit DESC;
