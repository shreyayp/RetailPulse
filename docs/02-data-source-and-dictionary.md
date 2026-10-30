# 02 — Data Source and Dictionary

## Source record
- Name: Retail Transactions and Stocks Data
- Contributor: Jimmy Smith
- Repository: Mendeley Data
- Version: 1
- Publication date: 27 April 2026
- DOI: 10.17632/27x8mjm8k4.1
- Licence: CC BY 4.0
- URL: https://data.mendeley.com/datasets/27x8mjm8k4/1

The record describes daily transaction-level sales and on-hand stock, a Division → Category → Subcategory → Segment hierarchy, 40 stores, 2,326 SKUs and three divisions. The published description lists a sales CSV (~37.3 MB) and inventory CSV (~95.4 MB).

## Data dictionary — canonical fields
The ETL maps source headers to these names. Confirm every mapping against the downloaded CSV headers.

| Canonical field | Meaning | Expected use |
|---|---|---|
| date | Business/stock date | Time analysis |
| store_id | Store identifier | Store analysis |
| sku_id | Stock keeping unit identifier | Product analysis |
| quantity | Units sold | Sales volume |
| sales | Sales amount | Revenue measure |
| unit_price | Unit selling price | Price analysis |
| cost | Cost amount, if present | Profitability |
| on_hand | Units in stock snapshot | Inventory analysis |
| division | Highest product hierarchy level | Product rollup |
| category | Product category | Product mix |
| subcategory | Product subcategory | Drill-down |
| segment | Product segment | Drill-down |

## Grain checks
Before joining sales and inventory, establish what one row represents in each file. Sales may be daily store-SKU aggregates rather than individual customer transactions. Inventory is a dated stock snapshot. Never join only on SKU if dates and stores are part of the grain; that can multiply rows.

## Profiling checklist
- Header and data types
- Min/max dates and gaps
- Row count and distinct store/SKU counts
- Null rates for keys and measures
- Duplicate business keys
- Negative quantities/amounts and their meaning
- Sales-to-quantity price consistency
- Inventory snapshot frequency
- Product hierarchy consistency

## Attribution
Smith, Jimmy (2026). *Retail Transactions and Stocks Data*, Version 1. Mendeley Data. DOI: 10.17632/27x8mjm8k4.1. CC BY 4.0.
