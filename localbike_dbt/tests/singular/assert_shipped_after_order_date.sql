select order_id, order_date, shipped_date
from {{ ref('fct_orders') }}
where shipped_date < order_date
