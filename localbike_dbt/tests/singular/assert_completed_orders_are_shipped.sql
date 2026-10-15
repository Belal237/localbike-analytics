-- A completed order without a shipping date would skew the delivery KPIs.

select order_id
from {{ ref('fct_orders') }}
where is_completed
  and shipped_date is null
