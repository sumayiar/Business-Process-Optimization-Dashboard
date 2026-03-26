WITH benchmarks AS (
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
    s.orders,
    s.net_revenue,
    s.gross_profit,
    s.margin_pct,
    s.avg_delivery_days,
    s.on_time_rate,
    s.return_rate,
    s.backorder_rate,
    s.avg_discount_pct,
    (
        CASE WHEN s.margin_pct < b.margin_benchmark THEN 1 ELSE 0 END
        + CASE WHEN s.on_time_rate < b.on_time_benchmark THEN 1 ELSE 0 END
        + CASE WHEN s.return_rate > b.return_benchmark THEN 1 ELSE 0 END
        + CASE WHEN s.backorder_rate > b.backorder_benchmark THEN 1 ELSE 0 END
        + CASE WHEN s.avg_delivery_days > b.delivery_benchmark THEN 1 ELSE 0 END
    ) AS issue_count,
    TRIM(
        CASE WHEN s.margin_pct < b.margin_benchmark THEN 'Low margin; ' ELSE '' END
        || CASE WHEN s.on_time_rate < b.on_time_benchmark THEN 'Late deliveries; ' ELSE '' END
        || CASE WHEN s.return_rate > b.return_benchmark THEN 'High returns; ' ELSE '' END
        || CASE WHEN s.backorder_rate > b.backorder_benchmark THEN 'Backorders; ' ELSE '' END
        || CASE WHEN s.avg_delivery_days > b.delivery_benchmark THEN 'Slow fulfillment; ' ELSE '' END
    ) AS issue_summary
FROM segment_scorecard s
CROSS JOIN benchmarks b
WHERE s.margin_pct < b.margin_benchmark
   OR s.on_time_rate < b.on_time_benchmark
   OR s.return_rate > b.return_benchmark
   OR s.backorder_rate > b.backorder_benchmark
   OR s.avg_delivery_days > b.delivery_benchmark
ORDER BY issue_count DESC, gross_profit ASC, net_revenue DESC;
