-- Sales activity per staff member over the whole period.

with orders as (
    select * from {{ ref('fct_orders') }}
),

per_staff as (
    select
        staff_id,
        count(*) as orders_handled,
        sum(case when is_completed then 1 else 0 end) as completed_orders,
        sum(case when order_status = 3 then 1 else 0 end) as rejected_orders,
        sum(case when is_completed then net_revenue else 0 end) as net_revenue
    from orders
    group by staff_id
)

select
    staffs.staff_id,
    staffs.staff_name,
    staffs.store_id,
    staffs.store_name,
    staffs.manager_name,
    staffs.is_active,
    coalesce(per_staff.orders_handled, 0) as orders_handled,
    coalesce(per_staff.completed_orders, 0) as completed_orders,
    coalesce(per_staff.rejected_orders, 0) as rejected_orders,
    round(per_staff.rejected_orders / nullif(per_staff.orders_handled, 0), 4) as rejection_rate,
    coalesce(per_staff.net_revenue, 0) as net_revenue,
    round(per_staff.net_revenue / nullif(per_staff.completed_orders, 0), 2) as avg_order_value
from {{ ref('dim_staffs') }} as staffs
left join per_staff
    on staffs.staff_id = per_staff.staff_id
