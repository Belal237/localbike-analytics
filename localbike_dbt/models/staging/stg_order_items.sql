select
    cast(order_id as integer) as order_id,
    cast(item_id as integer) as item_id,
    cast(product_id as integer) as product_id,
    cast(quantity as integer) as quantity,
    list_price,
    discount as discount_rate
from {{ ref('order_items') }}
