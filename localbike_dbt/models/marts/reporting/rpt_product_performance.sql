-- One row per product: what it sold, at which discount, and how much is still sitting in stock.
-- Products with stock but no sales are kept on purpose, they are the ones ops wants to see.

with products as (
    select * from {{ ref('dim_products') }}
),

sales as (
    select
        product_id,
        sum(case when is_completed then quantity else 0 end) as units_sold,
        count(distinct case when is_completed then order_id end) as orders_count,
        sum(case when is_completed then gross_revenue else 0 end) as gross_revenue,
        sum(case when is_completed then discount_amount else 0 end) as discount_amount,
        sum(case when is_completed then net_revenue else 0 end) as net_revenue,
        max(case when is_completed then order_date end) as last_sale_date,
        -- pending + processing orders: demand that is not invoiced yet
        sum(case when order_status in (1, 2) then quantity else 0 end) as units_in_open_orders
    from {{ ref('fct_sales') }}
    group by product_id
),

stock as (
    select
        product_id,
        sum(stock_quantity) as stock_quantity
    from {{ ref('stg_stocks') }}
    group by product_id
)

select
    products.product_id,
    products.product_name,
    products.brand_name,
    products.category_name,
    products.model_year,
    products.list_price,
    coalesce(sales.units_sold, 0) as units_sold,
    coalesce(sales.orders_count, 0) as orders_count,
    coalesce(sales.gross_revenue, 0) as gross_revenue,
    coalesce(sales.discount_amount, 0) as discount_amount,
    coalesce(sales.net_revenue, 0) as net_revenue,
    round(sales.discount_amount / nullif(sales.gross_revenue, 0), 4) as avg_discount_rate,
    sales.last_sale_date,
    coalesce(sales.units_in_open_orders, 0) as units_in_open_orders,
    coalesce(stock.stock_quantity, 0) as stock_quantity,
    round(coalesce(stock.stock_quantity, 0) * products.list_price, 2) as stock_value_at_list_price,
    rank() over (order by coalesce(sales.net_revenue, 0) desc) as revenue_rank
from products
left join sales
    on products.product_id = sales.product_id
left join stock
    on products.product_id = stock.product_id
