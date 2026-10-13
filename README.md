# Local Bike Analytics Engineering Project

A dbt-based analytics engineering project for Local Bike, focused on transforming raw retail data into a clean, testable and business-oriented data model for revenue and sales analysis.

## Project goal

Local Bike aims to improve sales performance, better understand product demand and optimize revenue across its stores. This project provides the analytical foundation needed to support operational decisions through a structured data model and dashboard.

## Business use cases

- Revenue analysis by store
- Contribution by product category
- Monthly sales trend monitoring
- Customer and order-level sales analysis
- Data quality checks for analytical reliability
- Business-ready reporting for operational teams

## Stack

- Python
- dbt
- DuckDB
- Plotly
- Pandas

## Repository structure

- `dataset/` — raw source files
- `localbike_dbt/` — dbt project and models
- `dashboard/` — dashboard generation script and HTML output

## Data model

The project follows a standard analytics engineering architecture:

- staging models for data cleaning and normalization
- mart models for analytical consumption
- quality tests for business and schema validation
- summary models for revenue and commercial insights

## Dashboard

The project includes a revenue dashboard built from the sales data, with visualizations for:

- revenue by store
- revenue by category
- monthly trend
- summary KPIs

## Local execution

```bash
cd localbike_dbt
. .venv/bin/activate
dbt seed --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
```

```bash
cd ..
python3 dashboard/localbike_dashboard.py
```

## Validation

The project has been validated locally with dbt:

- 9 seeds loaded successfully
- 13 models built successfully
- 16 data tests passed

## Notes

This project is designed as a lightweight analytics foundation for a small but growing retail business. It demonstrates a practical, production-minded workflow using modern analytics engineering tools while remaining easy to extend.
