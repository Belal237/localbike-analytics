# Local Bike, analytics engineering case

Final project of the DataBird Analytics Engineer track. Local Bike is a bike retailer with three
stores in the US (Santa Cruz CA, Baldwin NY, Rowlett TX). The brief: take their raw sales exports,
model them in dbt and give the operations team something they can actually use to sell more and
make more revenue.

The repo has three parts:

- `localbike_dbt/`: the dbt project (seeds, staging, intermediate, marts, tests, docs)
- `dashboard/`: a small Python script that reads the marts and builds an HTML dashboard
- `.github/workflows/`: CI that runs `dbt build` on every push so reviewers can see it's green

## Questions I wanted to answer

Before writing any SQL I listed what someone running the stores would want to know. Everything
in the marts comes from these five questions:

1. **Where does the revenue come from?** By store, by month, by category and brand.
2. **Are discounts worth it?** How much we give away, and whether it actually sells more units.
3. **Is the stock in the right place?** What sits on the shelves compared to what sells, and which
   products never sell at all.
4. **Do we deliver on time?** Days to ship and share of orders shipped after the promised date.
5. **How is the sales team doing?** Orders, revenue and rejection rate per staff member.

I also looked at customer retention, but there was nothing to show (see the findings).

## Data model

```
seeds (raw CSV)
  └── staging        stg_*            views, one per source table: renaming, typing, cleaning
        └── intermediate  int_sales__order_lines   view, revenue logic computed once
              └── marts/core       fct_sales, fct_orders, dim_customers, dim_products, dim_stores, dim_staffs
                    └── marts/reporting  rpt_store_monthly_sales, rpt_product_performance, rpt_staff_performance
```

A few choices worth explaining:

- **Revenue = completed orders only** (`order_status = 4`). Pending and processing orders are kept
  in the fact tables with an `is_completed` flag, because they matter for stock and workload, but
  they are not counted as revenue.
- **Net revenue** is `quantity * list_price - discount`. Amounts are rounded per line and the
  discount is subtracted after rounding, so `gross = discount + net` always adds up (there is a test
  for it).
- **The revenue logic lives in one place** (`int_sales__order_lines`). `fct_sales` and `fct_orders`
  both read from it, so they can't disagree. A singular test checks that their totals match.
- `fct_sales` carries product, brand, category and store names. Not very Kimball, but it means a BI
  tool can work from a single table, which is what the ops team will do in practice.
- The reporting models are the ones meant to be plugged into a dashboard. They are materialised as
  tables, everything upstream is a view.
- The export writes missing values as the text `'NULL'` (most customer phone numbers). A small
  macro, `clean_string`, turns those into real nulls in staging.

### Tests

120 data tests in total. Primary keys (unique + not null), every foreign key with `relationships`,
accepted values on statuses, a custom `non_negative` test on quantities and amounts, a custom
`unique_combination` test for composite keys, plus three singular tests:

- order totals in `fct_orders` match line totals in `fct_sales`
- no order is shipped before it was placed
- every completed order has a shipping date

I didn't add `dbt_utils` on purpose: the two generic tests I needed were a few lines each, and it
keeps the project runnable without `dbt deps`.

## What the data says

Figures cover January 2016 to March 2018, completed orders only.

- **$6.66M net revenue** on 1,445 orders, average basket **$4,611**.
- **Baldwin (NY) makes 71% of the revenue.** Average basket is about the same in the three stores
  ($4.4k to $5.0k), Baldwin simply gets much more traffic. Santa Cruz and Rowlett have room to grow
  on volume, not on basket size.
- **Discounts don't seem to drive volume.** Lines are sold at 5, 7, 10 or 20% off, in roughly equal
  shares, and the average quantity per line is ~1.5 at every level. That's **$775k** of discount
  over the period (10.4% of gross revenue) without a visible effect on units. Worth testing fewer,
  more targeted discounts.
- **Too much money is tied up in stock.** Stock on hand is worth ~$19.8M at list price, about three
  times the revenue of the whole period. Road bikes are the worst case: $6.8M of stock for $1.3M of
  revenue. 35 products are in stock but have never sold ($2.2M at list price).
- **About one order in three ships late** (shipped after the date promised to the customer):
  37% in Santa Cruz, 31% in Baldwin, 26% in Rowlett. For a brand built on customer experience this
  is probably the quickest thing to fix.
- **Rowlett rejects a lot more orders**: 9 to 12% of orders per staff member, against 1 to 4%
  elsewhere. Worth looking at why.
- **No repeat customers.** Every customer in the dataset has exactly one completed order. It could
  be how the data was generated, but if it's real, a loyalty or after-sales programme (servicing,
  accessories) is an obvious lever.
- **2018 is not a crash.** Completed orders stop at the end of March 2018; April orders are still
  pending or processing (~$818k) and the rest of the year only has rejected orders. Q1 2018 is
  actually up 7.7% on Q1 2017. Any chart by month has to show this, otherwise it looks like sales
  collapsed.

## Running it

### Locally with DuckDB (nothing else to install)

```bash
cd localbike_dbt
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

dbt build --profiles-dir .        # seeds + models + tests
dbt docs generate --profiles-dir . && dbt docs serve --profiles-dir .   # optional

cd ..
python dashboard/localbike_dashboard.py
open dashboard/output/localbike_dashboard.html
```

### On BigQuery

The SQL only uses cross-database macros (`dbt.date_trunc`, `dbt.datediff`, `dbt.type_string`), so
the same project runs on BigQuery with the `bigquery` target in `profiles.yml`:

```bash
pip install dbt-bigquery
gcloud auth application-default login
export GCP_PROJECT_ID=your-project-id
export BQ_LOCATION=EU               # optional, EU by default

dbt build --profiles-dir . --target bigquery
```

This creates the datasets `localbike_raw`, `localbike_staging`, `localbike_intermediate`,
`localbike_core` and `localbike_reporting`. The `rpt_*` tables in `localbike_reporting` are the
ones to connect to Looker Studio, Power BI or Metabase.

## Dashboard

`dashboard/localbike_dashboard.py` builds a single HTML page from the DuckDB marts: headline KPIs,
monthly revenue per store, revenue vs stock by category, late shipments per store, units per line by
discount level, staff activity and the list of products that never sold. The generated file is
committed in `dashboard/output/` so it can be opened without running anything.

## If I had more time

- Make `fct_sales` incremental on `order_date` once the data is loaded daily instead of as a one-off
  export.
- Schedule the run with Airflow (or simply dbt Cloud) and add source freshness checks.
- Rebuild the dashboard in Looker Studio on top of BigQuery so the ops team can filter it themselves.
- Get a cost price per product. Without it we only see revenue, not margin, and the discount
  question can't really be settled.
