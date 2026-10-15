select
    cast(product_id as integer) as product_id,
    {{ clean_string('product_name') }} as product_name,
    cast(brand_id as integer) as brand_id,
    cast(category_id as integer) as category_id,
    cast(model_year as integer) as model_year,
    list_price
from {{ ref('products') }}
