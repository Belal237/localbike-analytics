select
  order_id,
  item_id,
  product_id,
  quantity,
  list_price,
  discount
from {{ ref('order_items') }}
