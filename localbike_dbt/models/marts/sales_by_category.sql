select
  p.category_name,
  count(distinct f.order_id) as total_orders,
  sum(f.net_revenue) as net_revenue,
  avg(f.net_revenue) as avg_order_value
from {{ ref('fct_sales') }} f
left join {{ ref('dim_products') }} p on p.product_id = f.product_id
where f.order_status = 4
group by p.category_name
order by net_revenue desc
