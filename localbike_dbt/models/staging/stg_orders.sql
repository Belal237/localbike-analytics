select
  order_id,
  customer_id,
  order_status,
  cast(order_date as date) as order_date,
  cast(required_date as date) as required_date,
  cast(shipped_date as date) as shipped_date,
  store_id,
  staff_id
from {{ ref('orders') }}
