import pandas as pd
from src.etl import canonicalise

def test_canonicalise_maps_common_sales_columns():
    df = pd.DataFrame({"Transaction Date":["2026-01-01"],"Store":["S1"],"SKU":["P1"],"Units Sold":[2]})
    out = canonicalise(df)
    assert {"date","store_id","sku_id","quantity"}.issubset(out.columns)

def test_canonicalise_preserves_existing_canonical_names():
    df = pd.DataFrame({"date":["2026-01-01"],"store_id":["S1"],"sku_id":["P1"]})
    out = canonicalise(df)
    assert list(out.columns) == ["date","store_id","sku_id"]
