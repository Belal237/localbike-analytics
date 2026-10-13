select
  store_id,
  count(distinct order_id) as total_orders,
  sum(net_revenue) as net_revenue,
  avg(net_revenue) as avg_order_value
from {{ ref('fct_sales') }}
where order_status = 4
group by store_id
order by net_revenue desc
