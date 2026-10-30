# 05 — KPI and Visualisation Guide

## KPI rules
- Sales: sum the source sales amount; confirm whether it is gross or net.
- Units: sum quantity; inspect negative values and returns conventions.
- Gross profit: sales minus cost, only if cost exists and cost grain aligns.
- Gross margin: gross profit divided by sales.
- Inventory: on-hand quantity is a point-in-time stock measure, not a sales flow.
- Average selling price: sales divided by units, only for non-zero quantity and compatible units.

Do not label row count as order count unless an order/transaction identifier exists.

## Chart selection guide
| Question | Recommended visual | Why |
|---|---|---|
| Trend over time | Line/area | Time progression |
| Compare categories | Sorted bar | Accurate length comparison |
| Share of total | Donut/treemap | Part-to-whole, limited categories |
| Contribution concentration | Pareto | Ranked values + cumulative share |
| Relationship between two measures | Scatter | Correlation/outliers |
| Distribution | Histogram/box/violin | Spread and skew |
| Store × category | Heatmap | Pattern across two dimensions |
| Composition by period | Stacked bar/area | Mix over time |
| Exact values | Table/matrix | Audit and lookup |

Avoid pie charts with many categories. Use consistent units, labels, number formats and a common palette across every page.
