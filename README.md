# Business Process Optimization Project

## Overview
This project is a business analytics and process improvement case study focused on sales performance, cost efficiency, and logistics execution. The goal is to use data to identify where revenue is being lost, where costs are too high, and which operational bottlenecks are hurting profitability across regions and product categories.

You mentioned that you will keep working on this project until August 2026, so this README is written as a working guide, not just a summary. It should help you understand:
- what the project is trying to solve
- what data is included
- how the SQL analysis works
- how the Power BI dashboard should be built
- what has already been found
- how you can keep improving the project between now and August 2026

## Project Goal
The main objective is to evaluate business performance from both a commercial and operational perspective.

This project is designed to answer questions such as:
- Which regions and product categories generate the most revenue and profit?
- Which segments have weak profit margins even when sales are high?
- Where are logistics problems such as late delivery, backorders, and returns hurting performance?
- Which segments are underperforming compared with the overall business benchmark?
- What actions could improve efficiency, reduce cost, and increase profitability?

## Project Scope
This project covers four major areas:

1. Sales performance analysis
This includes revenue, discounting, units sold, product mix, and profit by region, category, channel, and customer segment.

2. Cost and profitability analysis
This includes product cost, shipping cost, handling cost, return cost, gross profit, and margin percentage.

3. Operational and logistics analysis
This includes delivery speed, late deliveries, backorders, return behavior, shipping mode, and warehouse performance.

4. Dashboard storytelling
This includes preparing clean, structured exports that can be used in Power BI to create interactive visuals for executives or stakeholders.

## Current Project Status
As of March 26, 2026, the project already includes:
- generated sales and operations datasets
- a reproducible Python pipeline
- a SQLite database for analysis
- SQL views and KPI queries
- dashboard-ready CSV exports
- an executive findings report
- a Power BI dashboard guide

This gives you a complete starting point. From here until August 2026, your work can focus on improving the business story, refining the visuals, adding deeper analysis, and making the project presentation stronger.

## Business Problem Statement
Many companies track sales and operations separately, which makes it harder to understand the real causes of poor performance. A region may look strong on revenue but weak on margin because of heavy discounting, expensive shipping, or high returns. Another segment may appear operationally stable but still underperform because the product mix is not profitable enough.

This project combines sales and logistics data in one analytical model so that profitability and operational efficiency can be evaluated together.

## Data Used In This Project
The project currently uses realistic synthetic business data. That means the data was generated to simulate a real company environment with patterns that make business sense, even though it is not sourced from a live company system.

The dataset covers:
- 18,000 orders
- order dates from January 1, 2024 through December 31, 2025
- five regions: Northeast, Southeast, Midwest, Southwest, West
- multiple product categories and subcategories
- multiple customer segments and sales channels
- logistics fields such as delivery time, shipping cost, returns, and backorders

This is useful because it lets you build a full analytics project structure even before you attach real-world data.

## Main Data Tables

### 1. `sales_orders`
This table stores the commercial side of the business.

Important fields:
- `order_id`: unique order identifier
- `order_date`: date of the order
- `region`: geographic sales region
- `state`: customer state
- `customer_segment`: Enterprise, SMB, or Consumer
- `sales_channel`: Direct Sales, Distributor, Online, or Retail
- `product_category`: high-level product group
- `product_subcategory`: subgroup within category
- `product_name`: individual product
- `units`: units sold
- `unit_price`: selling price per unit
- `discount_pct`: discount percentage applied
- `cogs_per_unit`: cost of goods sold per unit

### 2. `operations_logistics`
This table stores the fulfillment and logistics side of the business.

Important fields:
- `order_id`: link to the sales order
- `warehouse`: fulfillment center
- `shipping_mode`: Standard, Express, or Freight
- `planned_delivery_days`: expected delivery time
- `processing_days`: internal order processing time
- `actual_delivery_days`: real delivery time
- `shipping_cost`: transportation cost
- `handling_cost`: warehouse handling cost
- `return_flag`: whether the order was returned
- `return_reason`: reason for return
- `return_cost`: financial impact of the return
- `backorder_flag`: whether the order was delayed because of inventory shortage
- `on_time_flag`: whether delivery met the planned SLA

### 3. `fact_order_kpis`
This is the main analytical view created by joining sales and logistics data. It is the most important table for analysis and Power BI.

This view includes calculated fields such as:
- gross revenue
- discount amount
- net revenue
- product cost
- operating cost
- gross profit
- margin percentage
- delay days

### 4. `segment_scorecard`
This view summarizes performance by region and product category. It is useful for comparing segments and finding underperformers.

## Key KPIs In This Project
These are the main metrics you should understand and be able to explain:

- `Net Revenue`
  Revenue after discounts.

- `Gross Profit`
  Net revenue minus product cost, shipping cost, handling cost, and return cost.

- `Profit Margin %`
  Gross profit divided by net revenue.

- `On-Time Delivery %`
  Percentage of orders delivered on or before planned delivery time.

- `Return Rate %`
  Percentage of orders that were returned.

- `Backorder Rate %`
  Percentage of orders that experienced inventory shortages or delayed fulfillment.

- `Average Delivery Days`
  Average number of days required to complete delivery.

- `Average Discount %`
  Average discount applied across orders.

- `Profit Per Order`
  Average gross profit generated per order.

## Current Analytical Findings
The latest run of the project produced the following high-level results:

- total net revenue: $29.28M
- total gross profit: $9.35M
- average profit margin: 31.9%
- average delivery time: 5.0 days
- on-time delivery rate: 70.2%
- return rate: 7.1%

### Strongest segments
- Midwest Industrial
- Northeast Office Supplies
- Northeast Electronics

These segments perform well because they combine solid revenue with stronger margin and better delivery reliability than most weaker segments.

### Underperforming segments
- Southwest Furniture
- Southeast Electronics
- West Apparel
- Southeast Furniture

These segments were flagged because of one or more of the following:
- low margin
- high discount pressure
- slow fulfillment
- late deliveries
- backorders
- high returns

### Business interpretation
The project is not just about finding low sales. It is about showing that performance problems often come from the interaction between sales and operations.

Examples:
- A category can have high sales volume but weak profit because discounting and logistics costs are too high.
- A region can have acceptable revenue but still underperform because returns and backorders are increasing total cost.
- A segment can look profitable on paper but still create operational risk if delivery speed is consistently poor.

## Recommended Business Actions
Based on the current findings, the strongest recommendations are:
- tighten pricing and discount controls in low-margin segments
- improve inventory planning for categories with high backorder rates
- rebalance warehouse and carrier capacity for slow-fulfillment segments
- reduce returns through better packaging, order accuracy, product fit, and expectation-setting
- use high-performing segments as benchmarks for operational discipline and pricing strategy

## Project Structure

### Root-level files and folders
- `README.md`
  Main project guide and working reference.

- `data/`
  Stores raw files, exported dashboard tables, and the SQLite database.

- `scripts/`
  Contains the Python pipeline used to generate data and rebuild the project outputs.

- `sql/`
  Contains the schema, views, KPI queries, and export queries.

- `reports/`
  Stores written analysis outputs such as the business findings report.

- `docs/`
  Stores documentation such as the Power BI dashboard guide.

## Important Files To Know
- `scripts/build_project.py`
  Main pipeline script. Running this file rebuilds the project outputs.

- `sql/schema.sql`
  Creates the database tables.

- `sql/views.sql`
  Builds the KPI analysis layer.

- `sql/kpi_queries.sql`
  Contains the main SQL used to answer the business questions.

- `data/exports/order_kpi_fact.csv`
  Best file to use as the primary Power BI fact table.

- `reports/business_findings.md`
  Short executive summary of the project findings.

- `docs/powerbi_dashboard_guide.md`
  Step-by-step guidance for building the dashboard.

## How The Project Works

### Step 1. Generate and load data
The Python script creates synthetic datasets for sales and logistics and saves them into `data/raw/`.

### Step 2. Build the database
The same script creates a SQLite database in `data/business_process_optimization.sqlite`.

### Step 3. Create analytical views
The SQL files generate views that calculate revenue, cost, profit, margin, returns, and delivery KPIs.

### Step 4. Export dashboard tables
The pipeline exports clean CSV files into `data/exports/` for use in Power BI.

### Step 5. Write the findings report
The script automatically creates a written summary in `reports/business_findings.md`.

## How To Run The Project
Run this command from the project root:

```bash
python3 scripts/build_project.py
```

After running it, the project will regenerate:
- raw datasets
- SQLite database
- KPI exports
- findings report

## How To Explore The SQL
If you want to inspect the analysis directly in SQLite, you can run:

```bash
sqlite3 data/business_process_optimization.sqlite
```

Then inside SQLite:

```sql
SELECT * FROM fact_order_kpis LIMIT 10;
SELECT * FROM segment_scorecard ORDER BY gross_profit DESC LIMIT 10;
```

You can also run the main query file:

```bash
sqlite3 data/business_process_optimization.sqlite ".read sql/kpi_queries.sql"
```

## How To Use This In Power BI
The recommended Power BI workflow is:
- import `data/exports/order_kpi_fact.csv` as the main fact table
- create the DAX measures listed in `docs/powerbi_dashboard_guide.md`
- build an executive overview page
- build a logistics performance page
- build a segment drilldown page

Recommended visuals:
- KPI cards
- line charts for monthly trends
- bar charts for region and category comparisons
- matrix for detailed scorecards
- scatter plot for discount versus margin analysis
- decomposition tree or treemap for segment drilldown

## How To Talk About This Project
If you use this in a portfolio, presentation, or interview, the strongest project narrative is:

"I analyzed combined sales and operational data to identify where profitability was being reduced by discounting, fulfillment delays, backorders, and returns. I used SQL to build KPI views and Power BI to design dashboards that surfaced underperforming segments and supported data-driven recommendations for improving margin and efficiency."

You can also summarize your contribution using these four points:
- analyzed operational and sales datasets to identify inefficiencies in revenue, cost, and logistics performance
- built SQL queries to extract, aggregate, and evaluate key business KPIs across regions and product categories
- developed interactive Power BI dashboards to visualize trends, performance gaps, and operational bottlenecks
- identified underperforming segments and recommended data-driven strategies to improve profitability and efficiency

## Suggested Roadmap Through August 2026
Since you plan to keep working on this project until August 2026, this is a practical roadmap:

### March-April 2026
- understand the full project structure
- review the SQL logic and KPI definitions
- rebuild the project a few times so the workflow feels familiar
- import the exported data into Power BI
- create the first version of the dashboard

### May 2026
- improve dashboard design and storytelling
- add filters, drillthrough, tooltips, and conditional formatting
- refine the written explanation of business findings
- validate that each visual answers a real business question

### June 2026
- deepen the analysis
- add more benchmark comparisons
- create more focused views for returns, shipping cost, or channel performance
- strengthen the recommendations section with clearer business reasoning

### July 2026
- polish the final presentation
- improve layout, labeling, and consistency across dashboard pages
- prepare portfolio screenshots or a presentation deck
- tighten README language so it is easy for another person to understand quickly

### August 2026
- finalize the project story and dashboard
- make sure your metrics and findings are consistent everywhere
- document final takeaways
- prepare the project for submission, sharing, or interview discussion

## Good Next Improvements
If you want to make the project even stronger, these are good next upgrades:
- add a separate date dimension table export
- include warehouse-level performance analysis
- compare sales channels more deeply
- analyze customer segment profitability in more detail
- create a dedicated returns analysis page in Power BI
- add screenshots of your dashboard to the README later
- replace synthetic data with real data if that becomes available

## What To Read Next
- `reports/business_findings.md` for the current analysis summary
- `docs/powerbi_dashboard_guide.md` for dashboard construction
- `sql/kpi_queries.sql` for the main analytical logic
- `scripts/build_project.py` if you want to understand how the data and outputs are generated

## Final Note
This project already has a strong foundation. The main work from now until August 2026 is not starting from scratch, but improving clarity, depth, and presentation. If you keep the README, SQL, findings, and dashboard aligned, this can become a very solid portfolio project.
