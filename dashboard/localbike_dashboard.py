from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

base_dir = Path(__file__).resolve().parent.parent
data_dir = base_dir / "dataset"
out_dir = Path(__file__).resolve().parent / "output"
out_dir.mkdir(exist_ok=True)

orders = pd.read_csv(data_dir / "orders.csv")
order_items = pd.read_csv(data_dir / "order_items.csv")
products = pd.read_csv(data_dir / "products.csv")
stores = pd.read_csv(data_dir / "stores.csv")
categories = pd.read_csv(data_dir / "categories.csv")

order_items["gross_amount"] = order_items["quantity"] * order_items["list_price"]
order_items["discount_amount"] = order_items["gross_amount"] * order_items["discount"]
order_items["net_revenue"] = order_items["gross_amount"] * (1 - order_items["discount"])

sales = order_items.merge(
    orders[["order_id", "store_id", "order_date", "order_status"]],
    on="order_id",
    how="left",
)

sales = sales.merge(products[["product_id", "category_id"]], on="product_id", how="left")
sales = sales.merge(categories, on="category_id", how="left")
sales = sales.merge(stores[["store_id", "store_name", "city", "state"]], on="store_id", how="left")
sales["order_date"] = pd.to_datetime(sales["order_date"])

revenue_by_store = (
    sales[sales["order_status"] == 4]
    .groupby("store_name", as_index=False)["net_revenue"]
    .sum()
    .sort_values("net_revenue", ascending=False)
)

revenue_by_category = (
    sales[sales["order_status"] == 4]
    .groupby("category_name", as_index=False)["net_revenue"]
    .sum()
    .sort_values("net_revenue", ascending=False)
)

monthly_revenue = (
    sales[sales["order_status"] == 4]
    .assign(month=sales["order_date"].dt.to_period("M").astype(str))
    .groupby("month", as_index=False)["net_revenue"]
    .sum()
    .sort_values("month")
)

kpis = {
    "Total revenue": round(float(sales[sales["order_status"] == 4]["net_revenue"].sum()), 2),
    "Average order value": round(float(sales[sales["order_status"] == 4].groupby("order_id")["net_revenue"].sum().mean()), 2),
    "Best store": revenue_by_store.iloc[0]["store_name"],
    "Best category": revenue_by_category.iloc[0]["category_name"],
}

store_fig = px.bar(
    revenue_by_store,
    x="store_name",
    y="net_revenue",
    title="Revenue by store",
    color="store_name",
    template="plotly_white",
)

category_fig = px.bar(
    revenue_by_category.head(7),
    x="category_name",
    y="net_revenue",
    title="Revenue by bike category",
    color="category_name",
    template="plotly_white",
)

time_fig = px.line(
    monthly_revenue,
    x="month",
    y="net_revenue",
    title="Monthly revenue trend",
    markers=True,
    template="plotly_white",
)

kpi_cards = "".join(
    f"<div style='background:#f7f7f7;border:1px solid #ddd;padding:16px;border-radius:10px;min-width:200px;flex:1;'>"
    f"<div style='font-size:12px;color:#666;text-transform:uppercase;'>{name}</div>"
    f"<div style='font-size:28px;font-weight:700;margin-top:8px;'>{value}</div>"
    f"</div>"
    for name, value in kpis.items()
)

html = f"""
<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <title>Local Bike Dashboard</title>
  <script src='https://cdn.plot.ly/plotly-2.35.2.min.js'></script>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; background: #fafafa; color: #1c1c1c; }}
    h1 {{ margin-bottom: 10px; }}
    .cards {{ display: flex; gap: 16px; flex-wrap: wrap; margin: 24px 0; }}
    .chart-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 24px; }}
  </style>
</head>
<body>
  <h1>Local Bike - Revenue optimization dashboard</h1>
  <p>Business summary based on the Local Bike sales dataset.</p>
  <div class='cards'>{kpi_cards}</div>
  <div class='chart-grid'>
    <div id='storeChart'></div>
    <div id='categoryChart'></div>
    <div id='timeChart' style='grid-column: 1 / -1;'></div>
  </div>
  <script>
    const storeData = {store_fig.to_dict()};
    const categoryData = {category_fig.to_dict()};
    const timeData = {time_fig.to_dict()};
    Plotly.newPlot('storeChart', storeData.data, storeData.layout, {{responsive: true}});
    Plotly.newPlot('categoryChart', categoryData.data, categoryData.layout, {{responsive: true}});
    Plotly.newPlot('timeChart', timeData.data, timeData.layout, {{responsive: true}});
    window.addEventListener('resize', () => {{
      Plotly.Plots.resize('storeChart');
      Plotly.Plots.resize('categoryChart');
      Plotly.Plots.resize('timeChart');
    }});
  </script>
</body>
</html>
"""

output_path = out_dir / "localbike_dashboard.html"
output_path.write_text(html, encoding="utf-8")
print(f"Dashboard saved to: {output_path}")
