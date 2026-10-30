# 04 — Data Model and SQL

## Current logical model
- `fact_sales`: sales observations at source grain.
- `fact_inventory`: on-hand inventory observations at source grain.
- `data_quality_runs`: ingestion quality summaries.

A future star schema can include `dim_date`, `dim_store` and `dim_product`. Build dimensions only after confirming natural keys and hierarchy consistency.

## Grain
Write the grain in one sentence before each fact table is joined. Example: “One row per store, SKU and business date” must be confirmed, not assumed.

## SQL concepts
- `GROUP BY`: aggregate measures at category/store/month.
- `JOIN`: combine dimensions and facts using complete keys.
- `CASE WHEN`: classify business conditions.
- CTEs: separate query stages.
- Window functions: `ROW_NUMBER`, `RANK`, `SUM() OVER`, `LAG`.
- `NULLIF`: prevent divide-by-zero.
- Date functions: month-level aggregation and period comparison.

See `sql/analysis_queries.sql` for executable starter queries.
