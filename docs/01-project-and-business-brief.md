# 01 — Project and Business Brief

## Business context
Retail operators need a consistent view of sales performance, product mix, store contribution and inventory position. Source files are often operational exports; analysts must establish their grain, validate them and convert them into reusable metrics before visualising results.

## Objective
Build a reproducible analytics workflow that ingests published sales and inventory data, validates and standardises fields, loads an analytical store, and exposes decision-support views through Streamlit.

## Users
- Retail operations analyst
- Category manager
- Store manager
- Inventory planner
- Business/data analyst

## Questions the project should answer
1. How do sales and units trend over the observed date range?
2. Which divisions, categories, segments and SKUs contribute most to sales?
3. Which stores lead or lag on sales and gross profit (only when cost is present)?
4. How concentrated is sales contribution among the top SKUs?
5. What is the latest observed on-hand stock by store and product hierarchy?
6. Are the source data and transformations reliable enough to support the analysis?

## Out of scope until data supports it
Customer lifetime value, RFM, cohort retention, returns, discount effectiveness, geographic maps, stockout prediction and replenishment recommendations. These require fields or assumptions not guaranteed by the dataset description.

## Success criteria
- Repeatable local setup and ETL
- Documented source and licence
- Explicit source date range and row counts
- Tests for key transformations
- Reusable SQL analysis
- Consistent, accessible dashboard theme
- No fabricated data or unsupported business claims
