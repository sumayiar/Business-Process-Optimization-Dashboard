DROP VIEW IF EXISTS segment_scorecard;
DROP VIEW IF EXISTS fact_order_kpis;

CREATE VIEW fact_order_kpis AS
SELECT
    s.order_id,
    s.order_date,
    substr(s.order_date, 1, 7) AS year_month,
    s.region,
    s.state,
    s.customer_segment,
    s.sales_channel,
    s.product_category,
    s.product_subcategory,
    s.product_name,
    s.units,
    s.unit_price,
    s.discount_pct,
    ROUND(s.units * s.unit_price, 2) AS gross_revenue,
    ROUND(s.units * s.unit_price * s.discount_pct, 2) AS discount_amount,
    ROUND(s.units * s.unit_price * (1 - s.discount_pct), 2) AS net_revenue,
    ROUND(s.units * s.cogs_per_unit, 2) AS product_cost,
    o.shipping_cost,
    o.handling_cost,
    o.return_cost,
    ROUND(o.shipping_cost + o.handling_cost + o.return_cost, 2) AS operating_cost,
    ROUND(
        (s.units * s.unit_price * (1 - s.discount_pct))
        - ((s.units * s.cogs_per_unit) + o.shipping_cost + o.handling_cost + o.return_cost),
        2
    ) AS gross_profit,
    ROUND(
        (
            (s.units * s.unit_price * (1 - s.discount_pct))
            - ((s.units * s.cogs_per_unit) + o.shipping_cost + o.handling_cost + o.return_cost)
        ) * 1.0
        / NULLIF((s.units * s.unit_price * (1 - s.discount_pct)), 0),
        4
    ) AS margin_pct,
    o.warehouse,
    o.shipping_mode,
    o.planned_delivery_days,
    o.processing_days,
    o.actual_delivery_days,
    ROUND(o.actual_delivery_days - o.planned_delivery_days, 2) AS delay_days,
    o.return_flag,
    o.return_reason,
    o.return_cost > 0 AS has_return_cost,
    o.backorder_flag,
    o.on_time_flag
FROM sales_orders s
JOIN operations_logistics o
    ON s.order_id = o.order_id;

CREATE VIEW segment_scorecard AS
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
    ROUND(SUM(gross_profit) * 1.0 / NULLIF(COUNT(*), 0), 2) AS profit_per_order
FROM fact_order_kpis
GROUP BY region, product_category;
