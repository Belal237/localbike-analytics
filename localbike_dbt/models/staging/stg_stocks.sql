select
    cast(store_id as integer) as store_id,
    cast(product_id as integer) as product_id,
    cast(quantity as integer) as stock_quantity
from {{ ref('stocks') }}
