select
    cast(order_id as integer) as order_id,
    cast(customer_id as integer) as customer_id,
    cast(store_id as integer) as store_id,
    cast(staff_id as integer) as staff_id,
    cast(order_status as integer) as order_status,
    {{ order_status_label('order_status') }} as order_status_label,
    cast(order_date as date) as order_date,
    cast(required_date as date) as required_date,
    cast(shipped_date as date) as shipped_date
from {{ ref('orders') }}
