select
    cast(category_id as integer) as category_id,
    {{ clean_string('category_name') }} as category_name
from {{ ref('categories') }}
