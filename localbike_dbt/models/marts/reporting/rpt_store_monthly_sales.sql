-- Monthly revenue per store, completed orders only.
-- Main source for the "how are the stores doing" part of the dashboard.

with completed_orders as (
    select * from {{ ref('fct_orders') }}
    where is_completed
),

monthly as (
    select
        store_id,
        order_month,
        count(*) as orders_count,
        count(distinct customer_id) as customers_count,
        sum(units_count) as units_sold,
        sum(gross_revenue) as gross_revenue,
        sum(discount_amount) as discount_amount,
        sum(net_revenue) as net_revenue,
        sum(case when is_shipped_late then 1 else 0 end) as late_shipments_count
    from completed_orders
    group by store_id, order_month
)

select
    monthly.order_month,
    monthly.store_id,
    stores.store_name,
    monthly.orders_count,
    monthly.customers_count,
    monthly.units_sold,
    monthly.gross_revenue,
    monthly.discount_amount,
    monthly.net_revenue,
    monthly.late_shipments_count,
    round(monthly.net_revenue / nullif(monthly.orders_count, 0), 2) as avg_order_value,
    round(monthly.discount_amount / nullif(monthly.gross_revenue, 0), 4) as avg_discount_rate,
    round(monthly.late_shipments_count / nullif(monthly.orders_count, 0), 4) as late_shipment_rate
from monthly
left join {{ ref('dim_stores') }} as stores
    on monthly.store_id = stores.store_id
