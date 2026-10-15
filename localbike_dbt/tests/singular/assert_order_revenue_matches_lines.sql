-- fct_orders and fct_sales are built separately, the totals have to agree.

with from_orders as (
    select sum(net_revenue) as total from {{ ref('fct_orders') }}
),

from_lines as (
    select sum(net_revenue) as total from {{ ref('fct_sales') }}
)

select
    from_orders.total as orders_total,
    from_lines.total as lines_total
from from_orders
cross join from_lines
where abs(from_orders.total - from_lines.total) > 0.01
