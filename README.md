# RetailPulse — Retail Intelligence & Analytics Platform

RetailPulse is an end-to-end retail analytics portfolio project. It turns published daily sales and inventory records into a validated analytical warehouse, reusable SQL metrics and an interactive Streamlit/Plotly dashboard.

> **Data integrity rule:** this repository does not include fabricated transaction records. Download the source files and inspect the actual schema before interpreting any KPI. The app intentionally hides customer, returns, geography and inventory-cover analysis when the necessary fields are unavailable.

## 🚀 Live Dashboard

Explore the interactive RetailPulse dashboard:

**[Open RetailPulse Live Dashboard](https://retailpulse-shreya.streamlit.app/)**

Built with Python, Streamlit, Plotly, and SQL.

## 1. Dataset

**Retail Transactions and Stocks Data** — Jimmy Smith, Mendeley Data, Version 1, published 27 April 2026.  
Dataset page: https://data.mendeley.com/datasets/27x8mjm8k4/1  
DOI: https://doi.org/10.17632/27x8mjm8k4.1  
Licence: **CC BY 4.0** (attribute the dataset author and source).

The dataset description reports daily transaction-level sales and on-hand stock, a four-level product hierarchy (Division → Category → Subcategory → Segment), 40 retail storefronts, 2,326 SKUs and three divisions. Its two CSV files are approximately 37.3 MB (sales) and 95.4 MB (inventory).

The dataset was published in 2026; its publication year is not the same as its transaction observation period. RetailPulse reports the actual date range found in the downloaded files. It does not claim to contain a complete FY 2026–27.

## 2. Architecture

```text
Mendeley sales CSV ─┐
                    ├─> Raw layer ─> schema mapping & validation
Mendeley stock CSV ─┘                         |
                                              v
                                  Pandas transformation
                                              |
                                              v
                                  SQLite analytical warehouse
                                     |                 |
                                  SQL queries     Streamlit + Plotly
                                                       |
                                              Interactive analytics
```

## 3. Technology

- Python, Pandas, NumPy
- SQLite and SQL
- Streamlit and Plotly
- pytest
- Git / GitHub; Streamlit Community Cloud deployment

## 4. Quick start

### A. Create an environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate       # Windows
python -m pip install -r requirements.txt
```

### B. Download the source data

1. Open https://data.mendeley.com/datasets/27x8mjm8k4/1
2. Download the two CSV files: the sales/transactions file and the inventory/stock file.
3. Put both original CSVs in `data/raw/`. Keep their original filenames; the pipeline identifies sales/transaction and inventory/stock filenames.
4. Do not commit the raw files to GitHub; they are large. The dataset is available from its original source.

### C. Run the ETL

```bash
python -m src.etl
```

The pipeline creates:
- `data/processed/sales_clean.csv`
- `data/processed/inventory_clean.csv`
- `data/processed/retailpulse.db`
- `reports/latest_run.json`

The first run may reveal source-specific column names not covered by the initial alias map. If so, extend `ALIASES` in `src/etl.py` after inspecting the source headers. Do not silently rename fields based on assumptions.

### D. Launch the dashboard

```bash
python -m streamlit run app.py
```

### E. Run tests

```bash
python -m pytest -v
```

## 5. Dashboard

1. Executive Overview — sales, profit, margin, units and mix.
2. Sales Performance — time grain, trends, distribution and sales/units relationship.
3. Product Intelligence — category contribution, Pareto view and SKU table.
4. Store & Region — store ranking, sales/profit scatter and store-category heatmap.
5. Inventory Intelligence — latest on-hand inventory and category/store views.
6. Chart Explorer — selectable dimensions, measures, aggregation and chart types.
7. Data Explorer — searchable records and CSV export.
8. Project & Methodology — source, scope and analytical caveats.

The application uses one dark navy/teal design system across every page, sidebar, metric card, chart and table. Colours are configured in `.streamlit/config.toml` and the shared CSS in `app.py`.

## 6. KPI definitions

| KPI | Definition | Interpretation |
|---|---|---|
| Net sales | Sum of source sales amount | Sales value represented by the source field |
| Units sold | Sum of quantity | Volume sold |
| Gross profit | Sales less cost, only if cost exists | Profit before operating expenses |
| Gross margin % | Gross profit / sales × 100 | Profitability per sales dollar |
| Store count | Distinct store identifiers | Store coverage in the filtered dataset |
| SKU count | Distinct SKU identifiers | Product breadth in the filtered dataset |
| On-hand units | Sum of latest available stock quantity | Snapshot stock position |

**Important:** if source data lacks transaction/order IDs, transaction count is not inferred from row count. If it lacks cost, margin and profit should not be treated as validated economic measures. The ETL currently treats missing cost as zero for a provisional gross-profit calculation; before publishing profitability results, verify the source contains cost and update the mapping. Do not present this provisional value as actual gross profit.

## 7. Data model

- `fact_sales`: date, store, SKU, product hierarchy, quantity, sales, unit price, optional cost, derived gross profit and date attributes.
- `fact_inventory`: date, store, SKU, product hierarchy and on-hand quantity.
- `data_quality_runs`: source row counts and basic validation counts.

This is a practical analytical warehouse foundation. A later modelling phase can introduce conformed `dim_date`, `dim_store`, `dim_product` and surrogate keys after confirming source grain and identifiers.

## 8. Concepts to learn

- **ETL:** extract, transform, load; why raw and processed layers are separated.
- **Data profiling:** schema, types, nulls, duplicates, ranges and date coverage.
- **Fact vs dimension:** measurable business events versus descriptive entities.
- **Grain:** what one row represents; why it must be established before joins.
- **Aggregation:** sum, average, median and distinct counts.
- **Window functions:** ranking, running totals, period-over-period changes.
- **Pareto analysis:** concentration of sales among top SKUs.
- **Inventory snapshot:** stock-on-hand at a point in time; not interchangeable with sales flow.
- **Data visualisation:** select chart type based on the analytical question, not decoration.
- **Testing:** validate transformations, business rules and edge cases.

## 9. Limitations and next improvements

- Confirm source headers and grain before production use.
- Add explicit transaction/order count only if a transaction identifier exists.
- Add returns, discount, cost, customer segmentation, cohorts, store maps, stockout and days-of-cover analysis only when source fields support them.
- Add period comparison and forecasting only after establishing continuous, adequate historical coverage.
- For Streamlit Cloud, do not upload the 130+ MB raw files or SQLite database to GitHub. Use a compact, permitted processed extract or external storage if the full data exceeds deployment limits.

## 10. Attribution

Smith, Jimmy (2026). *Retail Transactions and Stocks Data*, Version 1. Mendeley Data. https://doi.org/10.17632/27x8mjm8k4.1. Licensed under CC BY 4.0. Please retain attribution and review the dataset record for any updated terms.

## 11. Repository structure

```text
RetailPulse/
├── app.py
├── config.py
├── requirements.txt
├── .streamlit/config.toml
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── reports/
├── sql/analysis_queries.sql
├── src/
│   ├── analytics.py
│   └── etl.py
└── tests/test_etl.py
```
