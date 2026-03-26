# Power BI Dashboard Guide

Use this guide to turn the exported KPI tables into a three-page interactive Power BI report.

## Recommended Data Imports
- Import `data/exports/order_kpi_fact.csv` as the primary fact table.
- Import `data/exports/underperforming_segments.csv` for annotation tables or issue callouts.
- Import `data/exports/regional_summary.csv` only if you want a lightweight executive summary table alongside the fact model.

## Core DAX Measures
Create these measures on top of `order_kpi_fact`.

```DAX
Total Revenue = SUM(order_kpi_fact[net_revenue])

Total Gross Profit = SUM(order_kpi_fact[gross_profit])

Profit Margin % = DIVIDE([Total Gross Profit], [Total Revenue])

Total Orders = COUNTROWS(order_kpi_fact)

Total Units = SUM(order_kpi_fact[units])

Average Delivery Days = AVERAGE(order_kpi_fact[actual_delivery_days])

On-Time Delivery % = AVERAGE(order_kpi_fact[on_time_flag])

Return Rate % = AVERAGE(order_kpi_fact[return_flag])

Backorder Rate % = AVERAGE(order_kpi_fact[backorder_flag])

Average Discount % = AVERAGE(order_kpi_fact[discount_pct])

Profit Per Order = DIVIDE([Total Gross Profit], [Total Orders])
```

## Date Table
Add a calendar table for trend analysis.

```DAX
Calendar =
ADDCOLUMNS(
    CALENDAR(MIN(order_kpi_fact[order_date]), MAX(order_kpi_fact[order_date])),
    "Year", YEAR([Date]),
    "Month Number", MONTH([Date]),
    "Month Name", FORMAT([Date], "MMM"),
    "Year Month", FORMAT([Date], "YYYY-MM")
)
```

Create a relationship from `Calendar[Date]` to `order_kpi_fact[order_date]`.

## Page 1: Executive Overview
- KPI cards: `Total Revenue`, `Total Gross Profit`, `Profit Margin %`, `On-Time Delivery %`, `Return Rate %`.
- Line chart: `Calendar[Year Month]` on the x-axis with `Total Revenue` and `Total Gross Profit` as values.
- Filled map or bar chart: `region` by `Total Gross Profit`.
- Matrix: `region` and `product_category` with `Total Revenue`, `Total Gross Profit`, `Profit Margin %`, and conditional formatting.
- Slicers: `region`, `product_category`, `customer_segment`, `sales_channel`.

## Page 2: Logistics Performance
- Clustered bar chart: `region` by `Average Delivery Days`.
- Stacked bar chart: `product_category` by `On-Time Delivery %` and `Backorder Rate %`.
- Scatter plot: `Average Discount %` on x-axis, `Profit Margin %` on y-axis, `product_category` as legend, `Total Revenue` as bubble size.
- Table: `region`, `product_category`, `Average Delivery Days`, `Backorder Rate %`, `Return Rate %`.

## Page 3: Segment Drilldown
- Decomposition tree or treemap: `Total Gross Profit` broken down by `region`, `product_category`, and `customer_segment`.
- Horizontal bar chart: `underperforming_segments[region]` plus `underperforming_segments[product_category]` ranked by `issue_count`.
- Detail table: `issue_summary`, `margin_pct`, `avg_delivery_days`, `on_time_rate`, `return_rate`, `backorder_rate`.
- Add a drillthrough page filtered by `region` and `product_category` if deeper operational review is needed.

## Design Notes
- Use red or amber highlights for `Return Rate %`, `Backorder Rate %`, and weak `Profit Margin %`.
- Add tooltips with `shipping_mode`, `warehouse`, and `customer_segment` to help explain operational drivers.
- Use bookmarks or a toggle button to switch between revenue-focused and logistics-focused views.

## Business Story To Emphasize
- Southwest Furniture and Southeast Electronics show the clearest combination of margin pressure and operational drag.
- West Apparel is a returns-driven inefficiency story rather than a pure revenue shortfall.
- Midwest Industrial and Northeast Office Supplies can serve as benchmark segments for pricing, fulfillment, and inventory discipline.
