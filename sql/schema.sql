DROP TABLE IF EXISTS operations_logistics;
DROP TABLE IF EXISTS sales_orders;

CREATE TABLE sales_orders (
    order_id TEXT PRIMARY KEY,
    order_date TEXT NOT NULL,
    region TEXT NOT NULL,
    state TEXT NOT NULL,
    customer_segment TEXT NOT NULL,
    sales_channel TEXT NOT NULL,
    product_category TEXT NOT NULL,
    product_subcategory TEXT NOT NULL,
    product_name TEXT NOT NULL,
    units INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    discount_pct REAL NOT NULL,
    cogs_per_unit REAL NOT NULL
);

CREATE TABLE operations_logistics (
    order_id TEXT PRIMARY KEY,
    warehouse TEXT NOT NULL,
    shipping_mode TEXT NOT NULL,
    planned_delivery_days INTEGER NOT NULL,
    processing_days REAL NOT NULL,
    actual_delivery_days REAL NOT NULL,
    shipping_cost REAL NOT NULL,
    handling_cost REAL NOT NULL,
    return_flag INTEGER NOT NULL,
    return_reason TEXT,
    return_cost REAL NOT NULL,
    backorder_flag INTEGER NOT NULL,
    on_time_flag INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES sales_orders(order_id)
);

CREATE INDEX idx_sales_orders_date ON sales_orders(order_date);
CREATE INDEX idx_sales_orders_region_category ON sales_orders(region, product_category);
CREATE INDEX idx_operations_logistics_flags ON operations_logistics(on_time_flag, return_flag, backorder_flag);
