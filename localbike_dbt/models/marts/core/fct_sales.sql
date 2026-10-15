-- Line-level sales fact. Product, store and staff labels are denormalised on purpose:
-- it lets the BI tool work off a single table without rebuilding joins.

with lines as (
    select * from {{ ref('int_sales__order_lines') }}
),

products as (
    select * from {{ ref('dim_products') }}
),

stores as (
    select * from {{ ref('dim_stores') }}
)

select
    cast(lines.order_id as {{ dbt.type_string() }})
        || '-' || cast(lines.item_id as {{ dbt.type_string() }}) as sales_line_id,
    lines.order_id,
    lines.item_id,
    lines.order_date,
    lines.order_month,
    lines.order_status,
    lines.order_status_label,
    lines.is_completed,
    lines.customer_id,
    lines.staff_id,
    lines.store_id,
    stores.store_name,
    lines.product_id,
    products.product_name,
    products.brand_name,
    products.category_name,
    products.model_year,
    lines.quantity,
    lines.list_price,
    lines.discount_rate,
    lines.gross_revenue,
    lines.discount_amount,
    lines.net_revenue
from lines
left join products
    on lines.product_id = products.product_id
left join stores
    on lines.store_id = stores.store_id
