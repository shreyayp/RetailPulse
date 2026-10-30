
"""RetailPulse ingestion, canonicalisation and warehouse loading."""

from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from config import RAW_DIR, PROCESSED_DIR, REPORTS_DIR, DB_PATH


# ---------------------------------------------------------
# 1. SOURCE COLUMN MAPPINGS
# ---------------------------------------------------------

ALIASES = {
    "date": [
        "date", "business_date", "transaction_date",
        "sales_date", "day", "start_date"
    ],
    "end_date": ["end_date"],
    "store_id": [
        "store_id", "store", "store_code",
        "location_id", "store_number"
    ],
    "sku_id": [
        "sku_id", "sku", "product_id", "product_no",
        "item_id", "item", "upc"
    ],
    "quantity": [
        "quantity", "qty", "qty_sold", "units",
        "units_sold", "sales_units", "unit_sales", "sales_qty"
    ],
    "sales": [
        "sales", "sales_amount", "net_sales", "revenue",
        "gross_sales", "dollar_sales", "total_sales"
    ],
    "unit_price": [
        "unit_price", "price", "selling_price",
        "retail_price", "avg_price"
    ],
    "on_hand": [
        "on_hand", "onhand", "stock_on_hand",
        "inventory_on_hand", "quantity_on_hand",
        "qty_on_hand", "stock", "units_on_hand"
    ],
    "division": [
        "division", "product_division", "department", "dept"
    ],
    "category": ["category", "product_category", "class"],
    "subcategory": [
        "subcategory", "product_subcategory", "sub_category"
    ],
    "segment": ["segment", "product_segment"],
    "cost": ["cost", "unit_cost", "cogs", "cost_amount"],
    "is_return": ["is_return", "return"],
    "return_reason": ["reason_of_return", "return_reason"],
}


# ---------------------------------------------------------
# 2. COLUMN STANDARDISATION
# ---------------------------------------------------------

def _norm(s: str) -> str:
    return re.sub(
        r"[^a-z0-9]+",
        "_",
        str(s).strip().lower()
    ).strip("_")


def canonicalise(df: pd.DataFrame) -> pd.DataFrame:
    """Map source column names to a stable analytical schema."""

    out = df.copy()
    out.columns = [_norm(c) for c in out.columns]

    rename = {}

    for target, candidates in ALIASES.items():
        if target in out.columns:
            continue

        for candidate in candidates:
            if candidate in out.columns:
                rename[candidate] = target
                break

    return out.rename(columns=rename)


# ---------------------------------------------------------
# 3. SOURCE FILE DISCOVERY
# ---------------------------------------------------------

def locate_csv(kind: str) -> Path:
    candidates = sorted(RAW_DIR.glob("*.csv"))

    keywords = (
        ("sales", "transaction")
        if kind == "sales"
        else ("inventory", "stock")
    )

    for path in candidates:
        if any(keyword in path.name.lower() for keyword in keywords):
            return path

    raise FileNotFoundError(
        f"No {kind} CSV found in {RAW_DIR}. "
        "Place the source sales and inventory CSV files in data/raw/."
    )


# ---------------------------------------------------------
# 4. SALES TRANSFORMATION
# ---------------------------------------------------------

def prepare_sales(path: Path) -> tuple[pd.DataFrame, dict]:

    raw = pd.read_csv(path, low_memory=False)
    df = canonicalise(raw)

    required = ["date", "store_id", "sku_id"]

    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(
            f"Sales file is missing required fields: {missing}. "
            f"Available columns: {list(df.columns)}"
        )

    if "quantity" not in df.columns and "sales" not in df.columns:
        raise ValueError(
            "Sales file needs a quantity or sales amount field."
        )

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for column in ["quantity", "sales", "unit_price", "cost"]:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    if "sales" not in df.columns:
        if "unit_price" not in df.columns:
            raise ValueError(
                "Could not derive sales: provide sales amount or unit_price."
            )

        df["sales"] = df["quantity"] * df["unit_price"]

    if "quantity" not in df.columns:
        if "unit_price" not in df.columns:
            df["quantity"] = np.nan
        else:
            df["quantity"] = (
                df["sales"] /
                df["unit_price"].replace(0, np.nan)
            )

    if "unit_price" not in df.columns:
        df["unit_price"] = (
            df["sales"] /
            df["quantity"].replace(0, np.nan)
        )

    # Preserve product hierarchy.
    for column in ["division", "category", "subcategory", "segment"]:
        if column not in df.columns:
            df[column] = "Unknown"

        df[column] = (
            df[column]
            .fillna("Unknown")
            .astype(str)
        )

    # COGS is a row-level amount in this dataset.
    if "cost" in df.columns:
        df["gross_profit"] = df["sales"] - df["cost"]
    else:
        df["gross_profit"] = np.nan

    # Time dimensions.
    df["year_month"] = df["date"].dt.to_period("M").astype(str)
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["weekday"] = df["date"].dt.day_name()

    df["gross_margin_pct"] = np.where(
        df["sales"] != 0,
        df["gross_profit"] / df["sales"] * 100,
        np.nan
    )

    df["store_id"] = df["store_id"].astype(str)
    df["sku_id"] = df["sku_id"].astype(str)

    quality = {
        "source_file": path.name,
        "rows_in": int(len(raw)),
        "rows_out": int(len(df)),
        "invalid_dates": int(df["date"].isna().sum()),
        "missing_store": int(df["store_id"].isna().sum()),
        "missing_sku": int(df["sku_id"].isna().sum()),
        "negative_quantity": int((df["quantity"] < 0).sum()),
        "negative_sales": int((df["sales"] < 0).sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    }

    df = df.dropna(
        subset=["date", "store_id", "sku_id"]
    )

    return df, quality


# ---------------------------------------------------------
# 5. INVENTORY TRANSFORMATION
# ---------------------------------------------------------

def prepare_inventory(path: Path) -> tuple[pd.DataFrame, dict]:

    raw = pd.read_csv(path, low_memory=False)
    df = canonicalise(raw)

    required = ["date", "store_id", "sku_id", "on_hand"]

    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(
            f"Inventory file is missing required fields: {missing}. "
            f"Available columns: {list(df.columns)}"
        )

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df["on_hand"] = pd.to_numeric(
        df["on_hand"],
        errors="coerce"
    )

    # Preserve the original end date, including 9999-12-31.
    if "end_date" in df.columns:
        df["end_date"] = df["end_date"].astype(str)

    # Convert useful numeric inventory measures.
    for column in [
        "stocks_selling_amount",
        "cost_of_stocks",
        "stock_unit_selling_price",
        "stock_unit_cost_price"
    ]:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    for column in ["division", "category", "subcategory", "segment"]:
        if column not in df.columns:
            df[column] = "Unknown"

        df[column] = (
            df[column]
            .fillna("Unknown")
            .astype(str)
        )

    df["store_id"] = df["store_id"].astype(str)
    df["sku_id"] = df["sku_id"].astype(str)

    quality = {
        "source_file": path.name,
        "rows_in": int(len(raw)),
        "rows_out": int(len(df)),
        "invalid_dates": int(df["date"].isna().sum()),
        "negative_on_hand": int((df["on_hand"] < 0).sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    }

    df = df.dropna(
        subset=["date", "store_id", "sku_id"]
    )

    return df, quality


# ---------------------------------------------------------
# 6. SQLITE WAREHOUSE LOADING
# ---------------------------------------------------------

def load_to_database(
    sales: pd.DataFrame,
    inventory: pd.DataFrame,
    sales_quality: dict,
    inventory_quality: dict
) -> None:
    """Load staging tables and atomically swap the live tables."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH, timeout=60) as conn:

        conn.execute("PRAGMA busy_timeout = 60000")
        conn.execute("PRAGMA journal_mode = WAL")

        # Build staging tables first.
        sales.to_sql(
            "_fact_sales_next",
            conn,
            if_exists="replace",
            index=False
        )

        inventory.to_sql(
            "_fact_inventory_next",
            conn,
            if_exists="replace",
            index=False
        )

        # Swap live tables in a transaction.
        conn.execute("BEGIN IMMEDIATE")

        try:
            conn.execute("DROP TABLE IF EXISTS fact_sales")
            conn.execute("DROP TABLE IF EXISTS fact_inventory")

            conn.execute(
                "ALTER TABLE _fact_sales_next RENAME TO fact_sales"
            )

            conn.execute(
                "ALTER TABLE _fact_inventory_next RENAME TO fact_inventory"
            )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        # Append data quality history.
        pd.DataFrame(
            [sales_quality, inventory_quality]
        ).to_sql(
            "data_quality_runs",
            conn,
            if_exists="append",
            index=False
        )


# ---------------------------------------------------------
# 7. MAIN ETL PIPELINE
# ---------------------------------------------------------

def run_pipeline() -> dict:

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Discover source files.
    sales_path = locate_csv("sales")
    inventory_path = locate_csv("inventory")

    # Extract and transform.
    sales, sales_quality = prepare_sales(sales_path)
    inventory, inventory_quality = prepare_inventory(inventory_path)

    # Save processed CSV files.
    sales.to_csv(
        PROCESSED_DIR / "sales_clean.csv",
        index=False
    )

    inventory.to_csv(
        PROCESSED_DIR / "inventory_clean.csv",
        index=False
    )

    # Load into SQLite.
    load_to_database(
        sales,
        inventory,
        sales_quality,
        inventory_quality
    )

    # Build execution report.
    result = {
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "SUCCESS",
        "sales": sales_quality,
        "inventory": inventory_quality,
        "sales_date_min": str(sales["date"].min()),
        "sales_date_max": str(sales["date"].max()),
        "stores": int(sales["store_id"].nunique()),
        "skus": int(sales["sku_id"].nunique()),
    }

    report_path = REPORTS_DIR / "latest_run.json"

    report_path.write_text(
        json.dumps(result, indent=2)
    )

    return result


# ---------------------------------------------------------
# 8. COMMAND-LINE EXECUTION
# ---------------------------------------------------------

if __name__ == "__main__":
    print(
        json.dumps(
            run_pipeline(),
            indent=2
        )
    )
