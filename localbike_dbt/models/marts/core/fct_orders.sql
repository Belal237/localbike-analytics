with orders as (
    select * from {{ ref('stg_orders') }}
),

order_totals as (
    select
        order_id,
        count(*) as lines_count,
        sum(quantity) as units_count,
        sum(gross_revenue) as gross_revenue,
        sum(discount_amount) as discount_amount,
        sum(net_revenue) as net_revenue
    from {{ ref('int_sales__order_lines') }}
    group by order_id
)

select
    orders.order_id,
    orders.customer_id,
    orders.store_id,
    orders.staff_id,
    orders.order_status,
    orders.order_status_label,
    orders.order_status = 4 as is_completed,
    orders.order_date,
    cast({{ dbt.date_trunc('month', 'orders.order_date') }} as date) as order_month,
    orders.required_date,
    orders.shipped_date,
    {{ dbt.datediff('orders.order_date', 'orders.shipped_date', 'day') }} as days_to_ship,
    case
        when orders.shipped_date is null then null
        else orders.shipped_date > orders.required_date
    end as is_shipped_late,
    coalesce(order_totals.lines_count, 0) as lines_count,
    coalesce(order_totals.units_count, 0) as units_count,
    coalesce(order_totals.gross_revenue, 0) as gross_revenue,
    coalesce(order_totals.discount_amount, 0) as discount_amount,
    coalesce(order_totals.net_revenue, 0) as net_revenue
from orders
left join order_totals
    on orders.order_id = order_totals.order_id
