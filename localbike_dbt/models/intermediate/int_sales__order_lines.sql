-- One row per order line, with the order context attached and the money columns computed once.
-- Every mart reads its revenue from here so the definitions can't drift between models.

with order_items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

lines as (
    select
        oi.order_id,
        oi.item_id,
        oi.product_id,
        o.customer_id,
        o.store_id,
        o.staff_id,
        o.order_status,
        o.order_status_label,
        o.order_status = 4 as is_completed,
        o.order_date,
        cast({{ dbt.date_trunc('month', 'o.order_date') }} as date) as order_month,
        o.required_date,
        o.shipped_date,
        oi.quantity,
        oi.list_price,
        oi.discount_rate,
        round(oi.quantity * oi.list_price, 2) as gross_revenue,
        round(oi.quantity * oi.list_price * oi.discount_rate, 2) as discount_amount
    from order_items as oi
    inner join orders as o
        on oi.order_id = o.order_id
)

select
    *,
    -- computed from the rounded amounts so that gross = discount + net holds exactly
    gross_revenue - discount_amount as net_revenue
from lines
