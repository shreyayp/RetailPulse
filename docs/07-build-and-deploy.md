# 07 — Build, Test and Deploy

## Local validation
1. Create virtual environment.
2. Install `requirements.txt`.
3. Place source files in `data/raw/`.
4. Run `python -m src.etl`.
5. Inspect `reports/latest_run.json`, output row counts and date range.
6. Run `python -m pytest -v`.
7. Launch `python -m streamlit run app.py`.
8. Compare dashboard totals with independent SQL totals.

## Streamlit Community Cloud
The raw source files are too large to commit to GitHub. Before deployment:
- Prepare a compact processed extract only if dataset licence and attribution requirements permit redistribution.
- Or store data in an accessible external data store and configure credentials with Streamlit Secrets.
- Do not commit secrets, large raw data or a local SQLite DB.
- Add source attribution and observation-period details to the app.
- Verify the app cold-starts and has a clear data-unavailable state.

## Release checklist
- [ ] Source attribution and licence included
- [ ] Dataset observation dates verified
- [ ] Required columns mapped from actual source headers
- [ ] Pipeline run succeeds
- [ ] No fabricated or unsupported metrics
- [ ] Tests pass
- [ ] SQL totals reconcile with Pandas
- [ ] Dashboard filters work across pages
- [ ] Download/export works
- [ ] Theme consistent on every page
- [ ] Git ignore excludes raw/processed files and secrets
