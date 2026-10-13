with order_items as (
  select * from {{ ref('stg_order_items') }}
),
orders as (
  select * from {{ ref('stg_orders') }}
)

select
  oi.order_id,
  oi.item_id,
  oi.product_id,
  o.customer_id,
  o.store_id,
  o.order_date,
  o.order_status,
  oi.quantity,
  oi.list_price,
  oi.discount,
  round(oi.quantity * oi.list_price, 2) as gross_revenue,
  round(oi.quantity * oi.list_price * oi.discount, 2) as discount_amount,
  round(oi.quantity * oi.list_price * (1 - oi.discount), 2) as net_revenue
from order_items oi
left join orders o on o.order_id = oi.order_id
