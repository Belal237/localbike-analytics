"""Builds the Local Bike dashboard as a standalone HTML page.

Reads the dbt marts from the local DuckDB file, so run `dbt build` first.
Usage (from the repo root):  python dashboard/localbike_dashboard.py
"""

import os
from pathlib import Path

import duckdb
import plotly.graph_objects as go
import plotly.io as pio

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.environ.get("DBT_DUCKDB_PATH", ROOT / "localbike_dbt" / "localbike.duckdb"))
OUT_PATH = Path(__file__).resolve().parent / "output" / "localbike_dashboard.html"

CORE = "main_core"
REPORTING = "main_reporting"

# Fixed colour per store so it never changes between charts.
STORE_COLORS = {
    "Baldwin Bikes": "#2a78d6",
    "Santa Cruz Bikes": "#eb6834",
    "Rowlett Bikes": "#1baf7a",
}
MAIN_COLOR = "#2a78d6"
SECOND_COLOR = "#eb6834"
GRID_COLOR = "#e6e5e1"
TEXT_COLOR = "#52514e"


def query(con, sql):
    return con.sql(sql).df()


def money(value):
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.0f}k"
    return f"${value:,.0f}"


def style(fig, title, height=380):
    fig.update_layout(
        title=dict(text=title, x=0, font=dict(size=16, color="#0b0b0b")),
        template="plotly_white",
        height=height,
        margin=dict(l=10, r=10, t=60, b=10),
        font=dict(family="Inter, Arial, sans-serif", color=TEXT_COLOR, size=12),
        plot_bgcolor="#fcfcfb",
        paper_bgcolor="#fcfcfb",
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="white", font_size=12),
        bargap=0.35,
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, zeroline=False)
    fig.update_yaxes(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, zeroline=False)
    return fig


def to_div(fig):
    return pio.to_html(fig, full_html=False, include_plotlyjs=False, config={"displayModeBar": False})


def html_table(df, columns):
    head = "".join(f"<th>{label}</th>" for label in columns.values())
    rows = ""
    for _, row in df.iterrows():
        rows += "<tr>" + "".join(f"<td>{row[col]}</td>" for col in columns) + "</tr>"
    return f"<table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>"


def main():
    if not DB_PATH.exists():
        raise SystemExit(f"{DB_PATH} not found. Run `dbt build --profiles-dir .` in localbike_dbt/ first.")

    con = duckdb.connect(str(DB_PATH), read_only=True)

    kpi = query(con, f"""
        select
            sum(net_revenue) filter (where is_completed) as net_revenue,
            count(*) filter (where is_completed) as completed_orders,
            sum(discount_amount) filter (where is_completed) as discount_amount,
            sum(gross_revenue) filter (where is_completed) as gross_revenue,
            avg(case when is_shipped_late then 1.0 else 0.0 end) filter (where is_completed) as late_rate,
            sum(net_revenue) filter (where order_status in (1, 2)) as open_orders_value,
            max(order_date) filter (where is_completed) as last_completed_date
        from {CORE}.fct_orders
    """).iloc[0]

    monthly = query(con, f"""
        select order_month, store_name, net_revenue
        from {REPORTING}.rpt_store_monthly_sales
        order by order_month
    """)

    store_totals = query(con, f"""
        select
            store_name,
            sum(net_revenue) as net_revenue,
            sum(late_shipments_count) / sum(orders_count) as late_rate
        from {REPORTING}.rpt_store_monthly_sales
        group by store_name
        order by net_revenue desc
    """)

    categories = query(con, f"""
        select
            category_name,
            sum(net_revenue) as net_revenue,
            sum(stock_value_at_list_price) as stock_value
        from {REPORTING}.rpt_product_performance
        group by category_name
        order by net_revenue
    """)

    discount = query(con, f"""
        select
            cast(round(discount_rate * 100) as integer) as discount_pct,
            avg(quantity) as avg_units,
            count(*) as lines
        from {CORE}.fct_sales
        where is_completed
        group by 1
        order by 1
    """)

    dead_stock = query(con, f"""
        select product_name, category_name, stock_quantity, stock_value_at_list_price
        from {REPORTING}.rpt_product_performance
        where units_sold = 0 and stock_quantity > 0
        order by stock_value_at_list_price desc
    """)

    staff = query(con, f"""
        select staff_name, store_name, completed_orders, rejected_orders, rejection_rate, net_revenue
        from {REPORTING}.rpt_staff_performance
        where orders_handled > 0
        order by net_revenue desc
    """)

    # ---- charts -------------------------------------------------------------

    trend = go.Figure()
    for store, color in STORE_COLORS.items():
        data = monthly[monthly["store_name"] == store]
        trend.add_trace(go.Scatter(
            x=data["order_month"], y=data["net_revenue"], name=store, mode="lines",
            line=dict(color=color, width=2),
            hovertemplate="%{x|%b %Y}<br>" + store + ": $%{y:,.0f}<extra></extra>",
        ))
        last = data.iloc[-1]
        trend.add_annotation(
            x=last["order_month"], y=last["net_revenue"], text=store.replace(" Bikes", ""),
            showarrow=False, xanchor="left", xshift=6, font=dict(size=11, color=TEXT_COLOR),
        )
    trend.add_vrect(
        x0="2018-04-01", x1="2018-12-31", fillcolor="#efeee9", line_width=0, layer="below",
        annotation_text="no completed orders after March 2018", annotation_position="top left",
        annotation_font=dict(size=11, color=TEXT_COLOR),
    )
    style(trend, "Monthly net revenue by store", height=420)
    trend.update_yaxes(tickprefix="$", tickformat="~s")
    trend.update_layout(hovermode="x unified")

    cat_fig = go.Figure()
    cat_fig.add_trace(go.Bar(
        y=categories["category_name"], x=categories["net_revenue"], orientation="h",
        name="Net revenue 2016 to 2018", marker_color=MAIN_COLOR,
        hovertemplate="%{y}<br>Revenue: $%{x:,.0f}<extra></extra>",
    ))
    cat_fig.add_trace(go.Bar(
        y=categories["category_name"], x=categories["stock_value"], orientation="h",
        name="Stock on hand (list price)", marker_color=SECOND_COLOR,
        hovertemplate="%{y}<br>Stock value: $%{x:,.0f}<extra></extra>",
    ))
    style(cat_fig, "Revenue vs stock value by category", height=420)
    cat_fig.update_layout(barmode="group", bargroupgap=0.08)
    cat_fig.update_xaxes(tickprefix="$", tickformat="~s")

    late_fig = go.Figure(go.Bar(
        x=store_totals["store_name"], y=store_totals["late_rate"], marker_color=MAIN_COLOR,
        text=[f"{v:.0%}" for v in store_totals["late_rate"]], textposition="outside",
        hovertemplate="%{x}<br>Shipped late: %{y:.1%}<extra></extra>",
    ))
    style(late_fig, "Share of orders shipped after the promised date")
    late_fig.update_yaxes(tickformat=".0%", range=[0, max(store_totals["late_rate"]) * 1.3])

    disc_fig = go.Figure(go.Bar(
        x=[f"{p}%" for p in discount["discount_pct"]], y=discount["avg_units"], marker_color=MAIN_COLOR,
        text=[f"{v:.2f}" for v in discount["avg_units"]], textposition="outside",
        customdata=discount["lines"],
        hovertemplate="Discount %{x}<br>Avg units per line: %{y:.2f}<br>%{customdata} lines<extra></extra>",
    ))
    style(disc_fig, "Average units per order line, by discount level")
    disc_fig.update_yaxes(range=[0, 2])
    disc_fig.update_xaxes(title_text="Discount granted")

    # ---- page ---------------------------------------------------------------

    share_top_store = store_totals.iloc[0]["net_revenue"] / store_totals["net_revenue"].sum()
    dead_value = dead_stock["stock_value_at_list_price"].sum()

    tiles = [
        ("Net revenue (completed orders)", money(kpi["net_revenue"])),
        ("Completed orders", f"{int(kpi['completed_orders']):,}"),
        ("Average order value", money(kpi["net_revenue"] / kpi["completed_orders"])),
        ("Average discount", f"{kpi['discount_amount'] / kpi['gross_revenue']:.1%}"),
        ("Orders shipped late", f"{kpi['late_rate']:.0%}"),
        ("Pending + processing orders", money(kpi["open_orders_value"])),
    ]
    tiles_html = "".join(
        f"<div class='tile'><div class='tile-label'>{label}</div><div class='tile-value'>{value}</div></div>"
        for label, value in tiles
    )

    dead_table = dead_stock.head(10).assign(
        stock_value_at_list_price=lambda d: d["stock_value_at_list_price"].map(lambda v: f"${v:,.0f}")
    )
    staff_table = staff.assign(
        rejection_rate=lambda d: d["rejection_rate"].map(lambda v: f"{v:.1%}"),
        net_revenue=lambda d: d["net_revenue"].map(lambda v: f"${v:,.0f}"),
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Local Bike Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  body {{ font-family: Inter, Arial, sans-serif; margin: 0; background: #f4f3ef; color: #0b0b0b; }}
  main {{ max-width: 1200px; margin: 0 auto; padding: 32px 16px 64px; }}
  h1 {{ margin: 0 0 4px; font-size: 26px; }}
  h2 {{ font-size: 18px; margin: 40px 0 12px; }}
  .sub {{ color: {TEXT_COLOR}; margin: 0; }}
  .tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; margin: 24px 0; }}
  .tile {{ background: #fcfcfb; border: 1px solid {GRID_COLOR}; border-radius: 10px; padding: 14px 16px; }}
  .tile-label {{ font-size: 12px; color: {TEXT_COLOR}; }}
  .tile-value {{ font-size: 26px; font-weight: 700; margin-top: 6px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 480px), 1fr)); gap: 16px; }}
  .card {{ background: #fcfcfb; border: 1px solid {GRID_COLOR}; border-radius: 10px; padding: 8px; overflow-x: auto; }}
  .wide {{ grid-column: 1 / -1; }}
  .notes {{ background: #fcfcfb; border-left: 3px solid {MAIN_COLOR}; padding: 4px 20px; border-radius: 4px; }}
  .notes li {{ margin: 8px 0; line-height: 1.5; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
  th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid {GRID_COLOR}; }}
  th {{ color: {TEXT_COLOR}; font-weight: 600; }}
  .table-title {{ font-weight: 600; padding: 8px 10px 4px; }}
</style>
</head>
<body>
<main>
  <h1>Local Bike, sales and operations</h1>
  <p class="sub">Built from the dbt marts. Revenue = completed orders only, Jan 2016 to {kpi['last_completed_date']:%b %Y}.</p>

  <div class="tiles">{tiles_html}</div>

  <div class="grid">
    <div class="card wide">{to_div(trend)}</div>
    <div class="card">{to_div(cat_fig)}</div>
    <div class="card">{to_div(late_fig)}</div>
    <div class="card">{to_div(disc_fig)}</div>
    <div class="card">
      <div class="table-title">Staff activity</div>
      {html_table(staff_table, {
          "staff_name": "Staff", "store_name": "Store", "completed_orders": "Completed",
          "rejected_orders": "Rejected", "rejection_rate": "Rejection rate", "net_revenue": "Net revenue",
      })}
    </div>
    <div class="card wide">
      <div class="table-title">Never sold but still in stock ({len(dead_stock)} products, {money(dead_value)} at list price), top 10</div>
      {html_table(dead_table, {
          "product_name": "Product", "category_name": "Category",
          "stock_quantity": "Units in stock", "stock_value_at_list_price": "Value at list price",
      })}
    </div>
  </div>

  <h2>What stands out</h2>
  <div class="notes"><ul>
    <li>{store_totals.iloc[0]['store_name']} brings in {share_top_store:.0%} of revenue. The two other stores
        have a similar basket size, they just get far fewer orders.</li>
    <li>Discounts don't seem to move volume: a line sold at 20% off has about the same number of units as one at 5%.
        That is {money(kpi['discount_amount'])} given away over the period with no visible effect on quantity.</li>
    <li>Road bikes have the largest stock value of all categories while ranking second in revenue.
        Together with the never-sold products above, there is a lot of cash sitting in the stores.</li>
    <li>Roughly one order in three ships after the date promised to the customer, in all three stores.</li>
    <li>2018 looks like a collapse on the chart, but it is a data cut-off: orders from April 2018 are still pending
        or processing ({money(kpi['open_orders_value'])}), not lost sales.</li>
  </ul></div>
</main>
</body>
</html>
"""

    OUT_PATH.parent.mkdir(exist_ok=True)
    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"Dashboard written to {OUT_PATH}")


if __name__ == "__main__":
    main()
