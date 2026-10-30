# 06 — RetailPulse Interview Guide

## 60–90 second project pitch
“RetailPulse is an end-to-end retail analytics project. I sourced published daily retail sales and inventory data, profiled the source schema, standardised the fields with Pandas, validated keys and measures, and loaded curated sales and inventory facts into SQLite. I wrote SQL queries for monthly sales, category contribution and store ranking, then built a Streamlit and Plotly dashboard with consistent global filters and business-focused visualisations. I documented the dataset, licence, grain, KPI definitions and data-quality limitations so that the insights are reproducible and not overstated.”

Adapt the pitch after the source files are actually profiled and the pipeline run has been verified.

## Data engineering questions
1. What is ETL? Explain each RetailPulse stage.
2. Why preserve raw files? Reproducibility, audit and reprocessing.
3. What is data grain? Why establish it before joining sales and inventory?
4. How do you handle missing dates and invalid keys?
5. What is idempotency? How does a replace/full-refresh load behave?
6. Why use SQLite here? What would make you choose a warehouse or DuckDB?
7. How would you process a 100 MB+ CSV efficiently? Chunking, types, Parquet, DuckDB.
8. How would you detect duplicate store-SKU-date rows?
9. How would you design incremental loads?
10. What is a fact table versus a dimension table?

## SQL questions
1. Calculate monthly sales and profit.
2. Rank categories by sales using `DENSE_RANK`.
3. Calculate running sales by month using `SUM() OVER`.
4. Compare current month with previous month using `LAG`.
5. Calculate each category's percentage of total sales.
6. Find top five SKUs within each division.
7. Detect duplicate business keys with `GROUP BY ... HAVING COUNT(*) > 1`.
8. Explain `WHERE` versus `HAVING`.
9. Explain inner, left and full joins.
10. Why can a many-to-many join inflate sales?

## Python/Pandas questions
1. `read_csv` options for large files.
2. `astype` versus `to_numeric`.
3. `to_datetime(errors="coerce")` and its trade-offs.
4. `groupby` and `agg`.
5. `merge` validation and join cardinality.
6. `isna`, `duplicated`, `drop_duplicates`.
7. Vectorisation versus row-wise `apply`.
8. Why use functions and modules instead of one large notebook?

## BI and visualisation questions
1. Why use a line chart for time series?
2. When is a treemap appropriate?
3. What does a Pareto chart communicate?
4. Why use a scatter plot for sales versus profit?
5. How do global filters affect KPI consistency?
6. What is a misleading chart? Discuss truncated axes and inconsistent units.
7. How do you choose a KPI and define its numerator/denominator?

## Business case prompts
- Sales are up but profit is down. What would you investigate? Price/mix, cost, discounting if available, and data definitions.
- One store has unusually high sales. What validation checks would you perform? Duplicate rows, date coverage, store key, outliers.
- Inventory is high but sales are low. What additional data is required before recommending action? Stock history, lead time, demand, safety stock, supplier constraints.
- Top 10 SKUs account for most sales. What does this imply? Concentration and assortment risk; investigate contribution and availability.

## Honest project limitations to communicate
- Customer segmentation requires a customer identifier.
- Returns analysis requires return/refund fields or documented negative-quantity semantics.
- Discount effectiveness requires list price/discount fields.
- Inventory cover requires aligned stock and demand windows, plus a defined calculation.
- Geographic analysis requires store coordinates or a reliable store-location dimension.
- A dataset publication date does not imply that observations cover the same calendar year.
