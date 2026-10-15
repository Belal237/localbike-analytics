# localbike_dbt

dbt project for the Local Bike case. The context, the modelling choices and the findings are in the
[main README](../README.md); this file is just a map of the folder.

```
seeds/                 raw CSV exports, loaded with `dbt seed`
models/
  staging/             stg_*  one view per source table
  intermediate/        int_sales__order_lines
  marts/core/          facts and dimensions
  marts/reporting/     rpt_* tables used by the dashboard
macros/                clean_string, order_status_label
tests/generic/         non_negative, unique_combination
tests/singular/        cross-model consistency checks
analyses/              ad hoc KPI query
```

Quick start (DuckDB):

```bash
pip install -r requirements.txt
dbt build --profiles-dir .
```

BigQuery: `dbt build --profiles-dir . --target bigquery` with `GCP_PROJECT_ID` set (see the main README).
