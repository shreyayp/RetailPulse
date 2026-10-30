# 03 — Architecture and ETL

## Layers
1. **Raw:** original downloaded CSV files, unchanged.
2. **Staging/standardised:** source headers normalised and mapped to canonical names.
3. **Validated:** date and business keys checked; invalid key rows excluded from analytical output and counted in quality metrics.
4. **Curated:** derived date attributes and provisional measures.
5. **Warehouse:** SQLite fact tables.
6. **Serving:** SQL queries and Streamlit/Plotly.

## ETL sequence
1. Locate sales and inventory CSVs by filename.
2. Read source files with Pandas.
3. Normalise column labels.
4. Map common aliases to canonical schema.
5. Parse dates and numeric measures.
6. Derive sales from quantity × unit price only when required inputs exist.
7. Derive gross profit only when cost exists; verify source semantics before publishing.
8. Add year/month/weekday attributes.
9. Capture row counts, invalid dates, negative measures and duplicate rows.
10. Persist clean extracts and load SQLite tables.

## Failure handling
Missing files, missing required keys and unsupported sales calculations raise explicit errors. The pipeline should fail visibly rather than guess a field. Extend `ALIASES` only after reviewing actual headers.

## Idempotency
The current starter pipeline replaces the fact tables on each full refresh. This avoids duplicate accumulation for full-file loads. Incremental loading requires a stable source key, load watermark and deduplication policy; it is a later enhancement.

## Performance
The provided CSVs are sizable. Keep raw files outside Git. For very large datasets, consider chunked ingestion and DuckDB/Parquet. SQLite is used here as a lightweight local analytical warehouse.
