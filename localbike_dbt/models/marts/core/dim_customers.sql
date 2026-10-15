-- Customer attributes plus their purchase history.
-- Only completed orders count towards revenue and order numbers.

with customers as (
    select * from {{ ref('stg_customers') }}
),

customer_orders as (
    select
        customer_id,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date,
        count(*) as completed_orders,
        sum(net_revenue) as lifetime_net_revenue
    from {{ ref('fct_orders') }}
    where is_completed
    group by customer_id
)

select
    customers.customer_id,
    customers.first_name || ' ' || customers.last_name as customer_name,
    customers.email,
    customers.phone,
    customers.city,
    customers.state,
    customers.zip_code,
    customer_orders.first_order_date,
    customer_orders.last_order_date,
    coalesce(customer_orders.completed_orders, 0) as completed_orders,
    coalesce(customer_orders.lifetime_net_revenue, 0) as lifetime_net_revenue,
    coalesce(customer_orders.completed_orders, 0) > 1 as is_repeat_customer
from customers
left join customer_orders
    on customers.customer_id = customer_orders.customer_id
