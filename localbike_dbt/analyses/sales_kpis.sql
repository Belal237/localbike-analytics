-- Headline numbers, completed orders only. Compile with `dbt compile` and run the SQL by hand.

select
    count(*) as completed_orders,
    sum(net_revenue) as net_revenue,
    round(sum(net_revenue) / count(*), 2) as avg_order_value,
    round(sum(discount_amount) / sum(gross_revenue), 4) as avg_discount_rate
from {{ ref('fct_orders') }}
where is_completed
