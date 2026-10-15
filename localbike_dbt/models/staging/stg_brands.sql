select
    cast(brand_id as integer) as brand_id,
    {{ clean_string('brand_name') }} as brand_name
from {{ ref('brands') }}
