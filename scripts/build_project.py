from __future__ import annotations

import csv
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
EXPORT_DIR = BASE_DIR / "data" / "exports"
REPORTS_DIR = BASE_DIR / "reports"
DB_PATH = BASE_DIR / "data" / "business_process_optimization.sqlite"

SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"
VIEWS_PATH = BASE_DIR / "sql" / "views.sql"
EXPORT_QUERY_DIR = BASE_DIR / "sql" / "export_queries"

SALES_COLUMNS = [
    "order_id",
    "order_date",
    "region",
    "state",
    "customer_segment",
    "sales_channel",
    "product_category",
    "product_subcategory",
    "product_name",
    "units",
    "unit_price",
    "discount_pct",
    "cogs_per_unit",
]

OPS_COLUMNS = [
    "order_id",
    "warehouse",
    "shipping_mode",
    "planned_delivery_days",
    "processing_days",
    "actual_delivery_days",
    "shipping_cost",
    "handling_cost",
    "return_flag",
    "return_reason",
    "return_cost",
    "backorder_flag",
    "on_time_flag",
]

REGIONS = {
    "Northeast": {
        "states": ["New York", "Massachusetts", "Pennsylvania"],
        "warehouse": "Newark DC",
        "weight": 0.22,
        "cost_factor": 1.03,
        "delivery_offset": 0,
    },
    "Southeast": {
        "states": ["Florida", "Georgia", "North Carolina"],
        "warehouse": "Atlanta DC",
        "weight": 0.21,
        "cost_factor": 0.99,
        "delivery_offset": 0,
    },
    "Midwest": {
        "states": ["Illinois", "Ohio", "Michigan"],
        "warehouse": "Chicago DC",
        "weight": 0.20,
        "cost_factor": 0.95,
        "delivery_offset": -1,
    },
    "Southwest": {
        "states": ["Texas", "Arizona", "New Mexico"],
        "warehouse": "Dallas DC",
        "weight": 0.18,
        "cost_factor": 1.10,
        "delivery_offset": 1,
    },
    "West": {
        "states": ["California", "Washington", "Colorado"],
        "warehouse": "Reno DC",
        "weight": 0.19,
        "cost_factor": 1.06,
        "delivery_offset": 1,
    },
}

MODE_CONFIG = {
    "Standard": {"days": 5, "cost_mult": 1.00},
    "Express": {"days": 3, "cost_mult": 1.35},
    "Freight": {"days": 7, "cost_mult": 1.55},
}

CUSTOMER_SEGMENTS = {
    "Electronics": {"Enterprise": 0.24, "SMB": 0.38, "Consumer": 0.38},
    "Furniture": {"Enterprise": 0.32, "SMB": 0.43, "Consumer": 0.25},
    "Office Supplies": {"Enterprise": 0.18, "SMB": 0.56, "Consumer": 0.26},
    "Apparel": {"Enterprise": 0.18, "SMB": 0.30, "Consumer": 0.52},
    "Industrial": {"Enterprise": 0.46, "SMB": 0.40, "Consumer": 0.14},
}

CHANNEL_WEIGHTS = {
    "Enterprise": {"Direct Sales": 0.55, "Distributor": 0.30, "Online": 0.10, "Retail": 0.05},
    "SMB": {"Online": 0.34, "Distributor": 0.31, "Direct Sales": 0.21, "Retail": 0.14},
    "Consumer": {"Online": 0.56, "Retail": 0.34, "Distributor": 0.05, "Direct Sales": 0.05},
}

REGION_CATEGORY_MULTIPLIER = {
    "Northeast": {"Office Supplies": 1.15, "Electronics": 1.05},
    "Southeast": {"Electronics": 1.28, "Apparel": 1.10},
    "Midwest": {"Industrial": 1.24, "Furniture": 0.95},
    "Southwest": {"Furniture": 1.26, "Electronics": 1.06},
    "West": {"Apparel": 1.30, "Electronics": 1.08},
}

SEGMENT_ADJUSTMENTS = {
    ("Southwest", "Furniture"): {
        "discount_delta": 0.035,
        "shipping_mult": 1.30,
        "delay_delta": 1.45,
        "backorder_delta": 0.09,
        "return_delta": 0.04,
        "cost_delta": 0.02,
    },
    ("West", "Apparel"): {
        "discount_delta": 0.015,
        "shipping_mult": 1.08,
        "delay_delta": 0.35,
        "backorder_delta": 0.02,
        "return_delta": 0.11,
        "cost_delta": 0.00,
    },
    ("Southeast", "Electronics"): {
        "discount_delta": 0.05,
        "shipping_mult": 1.07,
        "delay_delta": 0.75,
        "backorder_delta": 0.05,
        "return_delta": 0.03,
        "cost_delta": 0.015,
    },
    ("Midwest", "Industrial"): {
        "discount_delta": -0.02,
        "shipping_mult": 0.91,
        "delay_delta": -0.75,
        "backorder_delta": -0.03,
        "return_delta": -0.02,
        "cost_delta": -0.02,
    },
    ("Northeast", "Office Supplies"): {
        "discount_delta": -0.01,
        "shipping_mult": 0.95,
        "delay_delta": -0.20,
        "backorder_delta": -0.02,
        "return_delta": -0.01,
        "cost_delta": -0.01,
    },
}

CATEGORIES = {
    "Electronics": {
        "weight": 0.26,
        "cost_ratio": (0.61, 0.72),
        "bulkiness": 0.9,
        "base_discount": 0.09,
        "base_return": 0.05,
        "base_backorder": 0.06,
        "processing_base": 1.0,
        "return_loss": 0.18,
        "shipping_modes": {"Standard": 0.56, "Express": 0.32, "Freight": 0.12},
        "unit_ranges": {
            "Enterprise": (2, 12),
            "SMB": (1, 8),
            "Consumer": (1, 4),
        },
        "products": {
            "Laptops": [("Nimbus Laptop", 1120), ("ThinkCore Laptop", 980), ("Apex Workstation", 1340)],
            "Tablets": [("Orbit Tablet", 640), ("Astra Tablet", 580), ("FieldTab Pro", 720)],
            "Networking": [("Mesh Router", 240), ("Smart Switch", 310), ("Secure Gateway", 420)],
            "Accessories": [("Dock Station", 145), ("Pro Headset", 180), ("Conference Cam", 210)],
        },
    },
    "Furniture": {
        "weight": 0.17,
        "cost_ratio": (0.54, 0.66),
        "bulkiness": 1.85,
        "base_discount": 0.10,
        "base_return": 0.04,
        "base_backorder": 0.05,
        "processing_base": 1.4,
        "return_loss": 0.16,
        "shipping_modes": {"Standard": 0.18, "Express": 0.05, "Freight": 0.77},
        "unit_ranges": {
            "Enterprise": (2, 8),
            "SMB": (1, 6),
            "Consumer": (1, 3),
        },
        "products": {
            "Chairs": [("Ergo Chair", 280), ("Summit Chair", 360), ("Task Stool", 190)],
            "Desks": [("Modular Desk", 540), ("Lift Desk", 690), ("Studio Desk", 440)],
            "Storage": [("Filing Cabinet", 240), ("Wall Storage", 330), ("Mobile Pedestal", 180)],
        },
    },
    "Office Supplies": {
        "weight": 0.20,
        "cost_ratio": (0.41, 0.56),
        "bulkiness": 0.55,
        "base_discount": 0.06,
        "base_return": 0.02,
        "base_backorder": 0.03,
        "processing_base": 0.7,
        "return_loss": 0.12,
        "shipping_modes": {"Standard": 0.74, "Express": 0.17, "Freight": 0.09},
        "unit_ranges": {
            "Enterprise": (20, 140),
            "SMB": (12, 90),
            "Consumer": (5, 30),
        },
        "products": {
            "Paper": [("Copy Paper Pack", 18), ("Premium Paper Box", 52), ("Recycled Paper Pack", 22)],
            "Ink": [("Black Ink Set", 38), ("Color Ink Set", 52), ("Toner Cartridge", 84)],
            "Writing": [("Gel Pen Bundle", 16), ("Marker Kit", 24), ("Notebook Set", 28)],
            "Organizers": [("Desk Organizer", 32), ("Archive Bin", 48), ("Label Pack", 14)],
        },
    },
    "Apparel": {
        "weight": 0.18,
        "cost_ratio": (0.35, 0.49),
        "bulkiness": 0.45,
        "base_discount": 0.08,
        "base_return": 0.08,
        "base_backorder": 0.04,
        "processing_base": 0.8,
        "return_loss": 0.22,
        "shipping_modes": {"Standard": 0.72, "Express": 0.22, "Freight": 0.06},
        "unit_ranges": {
            "Enterprise": (8, 60),
            "SMB": (6, 45),
            "Consumer": (2, 20),
        },
        "products": {
            "Uniforms": [("Shift Uniform", 46), ("Service Polo", 32), ("Team Hoodie", 58)],
            "Safety Wear": [("Safety Vest", 26), ("Protective Jacket", 88), ("Hi-Vis Hoodie", 64)],
            "Branded Gear": [("Event Tee", 22), ("Embroidered Cap", 18), ("Quarter Zip", 44)],
        },
    },
    "Industrial": {
        "weight": 0.19,
        "cost_ratio": (0.48, 0.62),
        "bulkiness": 1.15,
        "base_discount": 0.07,
        "base_return": 0.03,
        "base_backorder": 0.05,
        "processing_base": 1.1,
        "return_loss": 0.15,
        "shipping_modes": {"Standard": 0.48, "Express": 0.10, "Freight": 0.42},
        "unit_ranges": {
            "Enterprise": (4, 28),
            "SMB": (3, 18),
            "Consumer": (1, 6),
        },
        "products": {
            "Tools": [("Torque Wrench", 180), ("Diagnostic Meter", 260), ("Inspection Kit", 140)],
            "Components": [("Hydraulic Valve", 320), ("Bearing Set", 92), ("Drive Assembly", 410)],
            "Maintenance": [("Lubricant Kit", 74), ("Seal Pack", 58), ("Filter Module", 132)],
        },
    },
}

EXPORTS = [
    ("order_kpi_fact.sql", "order_kpi_fact.csv"),
    ("monthly_kpis.sql", "monthly_kpis.csv"),
    ("region_category_performance.sql", "region_category_performance.csv"),
    ("regional_summary.sql", "regional_summary.csv"),
    ("underperforming_segments.sql", "underperforming_segments.csv"),
]


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def weighted_choice(rng: random.Random, choices: dict[str, float]) -> str:
    labels = list(choices.keys())
    weights = list(choices.values())
    return rng.choices(labels, weights=weights, k=1)[0]


def seasonality_multiplier(category: str, month: int) -> float:
    if category == "Electronics" and month in {11, 12}:
        return 1.25
    if category == "Furniture" and month in {4, 5, 6}:
        return 1.15
    if category == "Office Supplies" and month in {1, 8, 9}:
        return 1.16
    if category == "Apparel" and month in {10, 11, 12}:
        return 1.22
    if category == "Industrial" and month in {3, 6, 9}:
        return 1.08
    return 1.0


def weather_delay(region: str, month: int) -> float:
    if region == "Northeast" and month in {1, 2, 12}:
        return 0.35
    if region == "Midwest" and month in {1, 2, 12}:
        return 0.28
    if region == "Southeast" and month in {8, 9}:
        return 0.25
    return 0.0


def choose_category(rng: random.Random, region: str, month: int) -> str:
    weights = {}
    for category, config in CATEGORIES.items():
        regional_boost = REGION_CATEGORY_MULTIPLIER.get(region, {}).get(category, 1.0)
        weights[category] = config["weight"] * regional_boost * seasonality_multiplier(category, month)
    return weighted_choice(rng, weights)


def choose_units(rng: random.Random, category: str, customer_segment: str) -> int:
    low, high = CATEGORIES[category]["unit_ranges"][customer_segment]
    return rng.randint(low, high)


def choose_product(rng: random.Random, category: str) -> tuple[str, str, float]:
    subcategory = rng.choice(list(CATEGORIES[category]["products"].keys()))
    product_name, base_price = rng.choice(CATEGORIES[category]["products"][subcategory])
    return subcategory, product_name, float(base_price)


def discount_adjustment(customer_segment: str, sales_channel: str) -> float:
    segment_delta = {"Enterprise": 0.01, "SMB": 0.015, "Consumer": 0.03}[customer_segment]
    channel_delta = {"Direct Sales": 0.00, "Distributor": 0.01, "Online": 0.015, "Retail": 0.005}[sales_channel]
    return segment_delta + channel_delta


def return_reason(category: str, late_delivery: bool, backorder_flag: int, rng: random.Random) -> str:
    if late_delivery or backorder_flag:
        return "Late delivery"
    choices = {
        "Electronics": ["Compatibility issue", "Damaged in transit", "Setup difficulty"],
        "Furniture": ["Damaged in transit", "Assembly issue", "Color mismatch"],
        "Office Supplies": ["Order error", "Damaged packaging", "Incorrect item"],
        "Apparel": ["Size mismatch", "Style preference", "Color mismatch"],
        "Industrial": ["Specification mismatch", "Damaged in transit", "Incorrect component"],
    }
    return rng.choice(choices[category])


def generate_data(order_count: int = 18000, seed: int = 42) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rng = random.Random(seed)
    start_date = date(2024, 1, 1)
    end_date = date(2025, 12, 31)
    date_window = (end_date - start_date).days
    sales_rows: list[dict[str, object]] = []
    ops_rows: list[dict[str, object]] = []

    for order_number in range(1, order_count + 1):
        order_date = start_date + timedelta(days=rng.randint(0, date_window))
        region = weighted_choice(rng, {name: details["weight"] for name, details in REGIONS.items()})
        state = rng.choice(REGIONS[region]["states"])
        category = choose_category(rng, region, order_date.month)
        segment = weighted_choice(rng, CUSTOMER_SEGMENTS[category])
        sales_channel = weighted_choice(rng, CHANNEL_WEIGHTS[segment])
        subcategory, product_name, base_price = choose_product(rng, category)
        units = choose_units(rng, category, segment)

        adjustment = SEGMENT_ADJUSTMENTS.get(
            (region, category),
            {
                "discount_delta": 0.0,
                "shipping_mult": 1.0,
                "delay_delta": 0.0,
                "backorder_delta": 0.0,
                "return_delta": 0.0,
                "cost_delta": 0.0,
            },
        )
        category_config = CATEGORIES[category]
        price_noise = rng.uniform(0.92, 1.10)
        unit_price = round(base_price * price_noise, 2)

        discount_pct = clamp(
            category_config["base_discount"]
            + discount_adjustment(segment, sales_channel)
            + (0.01 if order_date.month in {11, 12} and category in {"Electronics", "Apparel"} else 0.0)
            + adjustment["discount_delta"]
            + rng.uniform(-0.015, 0.015),
            0.01,
            0.30,
        )

        cost_ratio = clamp(
            rng.uniform(*category_config["cost_ratio"]) + adjustment["cost_delta"],
            0.30,
            0.85,
        )
        cogs_per_unit = round(unit_price * cost_ratio, 2)

        shipping_mode = weighted_choice(rng, category_config["shipping_modes"])
        backorder_probability = clamp(
            category_config["base_backorder"]
            + (0.03 if seasonality_multiplier(category, order_date.month) > 1 else 0.0)
            + adjustment["backorder_delta"]
            + rng.uniform(-0.01, 0.012),
            0.01,
            0.32,
        )
        backorder_flag = int(rng.random() < backorder_probability)

        planned_delivery_days = max(
            2,
            MODE_CONFIG[shipping_mode]["days"] + REGIONS[region]["delivery_offset"],
        )
        processing_days = round(
            max(
                0.4,
                category_config["processing_base"]
                + rng.uniform(0.2, 1.1)
                + (0.45 * max(adjustment["delay_delta"], 0))
                + (rng.uniform(1.0, 2.2) if backorder_flag else 0.0),
            ),
            1,
        )

        delay_days = clamp(
            rng.gauss(-0.65, 0.9)
            + adjustment["delay_delta"]
            + (rng.uniform(1.0, 2.8) if backorder_flag else 0.0)
            + weather_delay(region, order_date.month),
            -1.5,
            5.5,
        )
        actual_delivery_days = round(max(1.0, planned_delivery_days + delay_days), 1)
        on_time_flag = int(actual_delivery_days <= planned_delivery_days)

        shipping_cost = round(
            (
                5.5
                + units * (0.55 + category_config["bulkiness"] * 1.15)
                + unit_price * 0.005
            )
            * MODE_CONFIG[shipping_mode]["cost_mult"]
            * REGIONS[region]["cost_factor"]
            * adjustment["shipping_mult"]
            * rng.uniform(0.92, 1.12),
            2,
        )
        handling_cost = round(
            (1.9 + units * 0.18 * category_config["bulkiness"]) * rng.uniform(0.94, 1.10)
            + (3.25 if backorder_flag else 0.0),
            2,
        )

        net_revenue = units * unit_price * (1 - discount_pct)
        return_probability = clamp(
            category_config["base_return"]
            + {"Enterprise": -0.005, "SMB": 0.01, "Consumer": 0.03}[segment]
            + {"Direct Sales": -0.005, "Distributor": 0.0, "Online": 0.02, "Retail": 0.01}[sales_channel]
            + (0.03 if actual_delivery_days - planned_delivery_days > 1.5 else 0.0)
            + adjustment["return_delta"]
            + rng.uniform(-0.01, 0.01),
            0.01,
            0.45,
        )
        return_flag = int(rng.random() < return_probability)
        return_cost = round(
            net_revenue
            * (
                category_config["return_loss"]
                + (0.04 if actual_delivery_days - planned_delivery_days > 1.5 else 0.0)
                + (0.03 if category == "Apparel" else 0.0)
            )
            if return_flag
            else 0.0,
            2,
        )
        issue_reason = return_reason(
            category,
            actual_delivery_days - planned_delivery_days > 1.5,
            backorder_flag,
            rng,
        ) if return_flag else ""

        order_id = f"ORD-{order_number:05d}"
        sales_rows.append(
            {
                "order_id": order_id,
                "order_date": order_date.isoformat(),
                "region": region,
                "state": state,
                "customer_segment": segment,
                "sales_channel": sales_channel,
                "product_category": category,
                "product_subcategory": subcategory,
                "product_name": product_name,
                "units": units,
                "unit_price": unit_price,
                "discount_pct": round(discount_pct, 4),
                "cogs_per_unit": cogs_per_unit,
            }
        )
        ops_rows.append(
            {
                "order_id": order_id,
                "warehouse": REGIONS[region]["warehouse"],
                "shipping_mode": shipping_mode,
                "planned_delivery_days": planned_delivery_days,
                "processing_days": processing_days,
                "actual_delivery_days": actual_delivery_days,
                "shipping_cost": shipping_cost,
                "handling_cost": handling_cost,
                "return_flag": return_flag,
                "return_reason": issue_reason,
                "return_cost": return_cost,
                "backorder_flag": backorder_flag,
                "on_time_flag": on_time_flag,
            }
        )

    return sales_rows, ops_rows


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def load_database(sales_rows: list[dict[str, object]], ops_rows: list[dict[str, object]]) -> sqlite3.Connection:
    if DB_PATH.exists():
        DB_PATH.unlink()

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    connection.executemany(
        """
        INSERT INTO sales_orders (
            order_id, order_date, region, state, customer_segment, sales_channel,
            product_category, product_subcategory, product_name, units,
            unit_price, discount_pct, cogs_per_unit
        ) VALUES (
            :order_id, :order_date, :region, :state, :customer_segment, :sales_channel,
            :product_category, :product_subcategory, :product_name, :units,
            :unit_price, :discount_pct, :cogs_per_unit
        )
        """,
        sales_rows,
    )
    connection.executemany(
        """
        INSERT INTO operations_logistics (
            order_id, warehouse, shipping_mode, planned_delivery_days, processing_days,
            actual_delivery_days, shipping_cost, handling_cost, return_flag, return_reason,
            return_cost, backorder_flag, on_time_flag
        ) VALUES (
            :order_id, :warehouse, :shipping_mode, :planned_delivery_days, :processing_days,
            :actual_delivery_days, :shipping_cost, :handling_cost, :return_flag, :return_reason,
            :return_cost, :backorder_flag, :on_time_flag
        )
        """,
        ops_rows,
    )
    connection.executescript(VIEWS_PATH.read_text(encoding="utf-8"))
    connection.commit()
    return connection


def export_query(connection: sqlite3.Connection, query_path: Path, output_path: Path) -> None:
    query = query_path.read_text(encoding="utf-8")
    cursor = connection.execute(query)
    rows = cursor.fetchall()
    headers = [column[0] for column in cursor.description]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def write_findings(connection: sqlite3.Connection) -> None:
    overall = connection.execute(
        """
        SELECT
            COUNT(*) AS order_count,
            ROUND(SUM(net_revenue), 2) AS total_revenue,
            ROUND(SUM(gross_profit), 2) AS total_profit,
            ROUND(SUM(gross_profit) * 1.0 / NULLIF(SUM(net_revenue), 0), 4) AS margin_pct,
            ROUND(AVG(on_time_flag), 4) AS on_time_rate,
            ROUND(AVG(return_flag), 4) AS return_rate,
            ROUND(AVG(actual_delivery_days), 2) AS avg_delivery_days
        FROM fact_order_kpis
        """
    ).fetchone()

    best_region = connection.execute(
        """
        SELECT region, net_revenue, gross_profit, margin_pct, on_time_rate
        FROM (
            SELECT
                region,
                ROUND(SUM(net_revenue), 2) AS net_revenue,
                ROUND(SUM(gross_profit), 2) AS gross_profit,
                ROUND(SUM(gross_profit) * 1.0 / NULLIF(SUM(net_revenue), 0), 4) AS margin_pct,
                ROUND(AVG(on_time_flag), 4) AS on_time_rate
            FROM fact_order_kpis
            GROUP BY region
        )
        ORDER BY gross_profit DESC
        LIMIT 1
        """
    ).fetchone()

    top_segments = connection.execute(
        """
        SELECT region, product_category, net_revenue, gross_profit, margin_pct, on_time_rate
        FROM segment_scorecard
        ORDER BY gross_profit DESC
        LIMIT 3
        """
    ).fetchall()

    underperformers = connection.execute(
        (EXPORT_QUERY_DIR / "underperforming_segments.sql").read_text(encoding="utf-8")
    ).fetchall()

    recommendations: list[str] = []
    for row in underperformers[:3]:
        issue_summary = row["issue_summary"]
        if "Low margin" in issue_summary:
            recommendations.append(
                f"Review pricing and discount controls for {row['region']} {row['product_category']} to protect margin leakage."
            )
        if "Late deliveries" in issue_summary or "Slow fulfillment" in issue_summary:
            recommendations.append(
                f"Rebalance inventory and carrier capacity for {row['region']} {row['product_category']} to shorten delivery cycles."
            )
        if "Backorders" in issue_summary:
            recommendations.append(
                f"Increase safety stock and supplier lead-time monitoring for {row['region']} {row['product_category']}."
            )
        if "High returns" in issue_summary:
            recommendations.append(
                f"Reduce returns in {row['region']} {row['product_category']} through packaging, fit, and order-accuracy improvements."
            )

    deduped_recommendations = []
    for recommendation in recommendations:
        if recommendation not in deduped_recommendations:
            deduped_recommendations.append(recommendation)

    lines = [
        "# Business Findings",
        "",
        "## Executive Summary",
        (
            f"- Generated and analyzed {overall['order_count']:,} orders covering 2024-01-01 through 2025-12-31."
        ),
        (
            f"- Total net revenue reached ${overall['total_revenue']:,.2f} with ${overall['total_profit']:,.2f} in gross profit "
            f"and a {overall['margin_pct'] * 100:.1f}% profit margin."
        ),
        (
            f"- Logistics performance averaged {overall['avg_delivery_days']:.1f} delivery days with "
            f"{overall['on_time_rate'] * 100:.1f}% on-time fulfillment and a {overall['return_rate'] * 100:.1f}% return rate."
        ),
        (
            f"- {best_region['region']} led all regions with ${best_region['gross_profit']:,.2f} in gross profit "
            f"at a {best_region['margin_pct'] * 100:.1f}% margin."
        ),
        "",
        "## Strongest Segments",
    ]

    for row in top_segments:
        lines.append(
            (
                f"- {row['region']} {row['product_category']} delivered ${row['gross_profit']:,.2f} in profit "
                f"on ${row['net_revenue']:,.2f} of revenue with a {row['margin_pct'] * 100:.1f}% margin "
                f"and {row['on_time_rate'] * 100:.1f}% on-time delivery."
            )
        )

    lines.extend(["", "## Underperforming Segments"])
    for row in underperformers[:4]:
        lines.append(
            (
                f"- {row['region']} {row['product_category']} posted ${row['gross_profit']:,.2f} in profit "
                f"at a {row['margin_pct'] * 100:.1f}% margin. Key issues: {row['issue_summary'].strip('; ')}."
            )
        )

    lines.extend(["", "## Recommended Actions"])
    for recommendation in deduped_recommendations[:5]:
        lines.append(f"- {recommendation}")

    lines.extend(
        [
            "",
            "## Files for Dashboarding",
            "- `data/exports/order_kpi_fact.csv` is the primary Power BI import table.",
            "- `data/exports/monthly_kpis.csv`, `regional_summary.csv`, and `underperforming_segments.csv` support executive views and annotations.",
        ]
    )

    findings_path = REPORTS_DIR / "business_findings.md"
    findings_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    sales_rows, ops_rows = generate_data()
    write_csv(RAW_DIR / "sales_orders.csv", sales_rows, SALES_COLUMNS)
    write_csv(RAW_DIR / "operations_logistics.csv", ops_rows, OPS_COLUMNS)

    connection = load_database(sales_rows, ops_rows)
    try:
        for query_name, export_name in EXPORTS:
            export_query(connection, EXPORT_QUERY_DIR / query_name, EXPORT_DIR / export_name)
        write_findings(connection)
    finally:
        connection.close()

    print("Project pipeline completed.")
    print(f"Raw data: {RAW_DIR}")
    print(f"SQLite database: {DB_PATH}")
    print(f"Dashboard exports: {EXPORT_DIR}")
    print(f"Findings report: {REPORTS_DIR / 'business_findings.md'}")


if __name__ == "__main__":
    main()
