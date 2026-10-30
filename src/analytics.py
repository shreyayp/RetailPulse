
"""Reusable business metrics and cached data access for RetailPulse."""

import sqlite3
import pandas as pd
import streamlit as st

from config import DB_PATH


def get_connection():
    """Open a short-lived SQLite connection with a lock timeout."""
    con = sqlite3.connect(DB_PATH, timeout=60)
    con.execute("PRAGMA busy_timeout = 60000")
    return con


@st.cache_data(ttl=300, show_spinner=False)
def load_sales():
    if not DB_PATH.exists():
        return pd.DataFrame()

    try:
        with get_connection() as con:
            df = pd.read_sql_query(
                "SELECT * FROM fact_sales",
                con,
                parse_dates=["date"]
            )
        return df
    except (sqlite3.Error, pd.errors.DatabaseError):
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def load_inventory():
    if not DB_PATH.exists():
        return pd.DataFrame()

    try:
        with get_connection() as con:
            df = pd.read_sql_query(
                "SELECT * FROM fact_inventory",
                con,
                parse_dates=["date"]
            )
        return df
    except (sqlite3.Error, pd.errors.DatabaseError):
        return pd.DataFrame()


def kpis(df):
    if df.empty:
        return {
            "sales": 0,
            "units": 0,
            "profit": 0,
            "margin": 0,
            "orders": 0,
            "stores": 0,
            "skus": 0
        }

    sales = float(df["sales"].sum()) if "sales" in df else 0
    units = float(df["quantity"].sum()) if "quantity" in df else 0
    profit = float(df["gross_profit"].sum()) if "gross_profit" in df else 0
    margin = profit / sales * 100 if sales else 0

    return {
        "sales": sales,
        "units": units,
        "profit": profit,
        "margin": margin,
        "orders": int(df["transaction_id"].nunique())
                  if "transaction_id" in df else len(df),
        "stores": int(df["store_id"].nunique())
                  if "store_id" in df else 0,
        "skus": int(df["sku_id"].nunique())
                if "sku_id" in df else 0
    }
