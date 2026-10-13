# Local Bike Analytics Project

This dbt project models the Local Bike dataset to support revenue optimization and operational analysis.

## Objective

The goal is to transform the raw sales data into a clean, testable warehouse model that helps the operations team answer strategic questions such as:

- Which store generates the most revenue?
- Which product categories have the strongest margin and demand?
- Which customers and products should be prioritized for campaigns?
- How do revenues evolve over time and by store?

## Dataset

The raw CSV files are stored in the `seeds/` folder and correspond to the bicycle retail data of Local Bike.

## dbt structure

- `models/staging`: light cleaning and renaming of source data
- `models/marts`: business-ready tables for dashboards and analysis
- `tests`: schema and data quality tests

## Local execution

```bash
cd localbike_dbt
python3 -m pip install -r requirements.txt
python3 -m dbt --version
dbt seed --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
```

## Dashboard

A lightweight dashboard can be generated from the same data with:

```bash
cd dashboard
python3 localbike_dashboard.py
```

The resulting HTML file is saved in `dashboard/output/localbike_dashboard.html`.
