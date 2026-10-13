select
  count(distinct order_id) as total_orders,
  sum(quantity * list_price * (1 - discount)) as net_revenue,
  avg(quantity * list_price * (1 - discount)) as avg_order_value
from {{ ref('fct_sales') }}
