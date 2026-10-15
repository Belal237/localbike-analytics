select
    cast(store_id as integer) as store_id,
    {{ clean_string('store_name') }} as store_name,
    {{ clean_string('phone') }} as phone,
    lower({{ clean_string('email') }}) as email,
    {{ clean_string('street') }} as street,
    {{ clean_string('city') }} as city,
    {{ clean_string('state') }} as state,
    {{ clean_string('zip_code') }} as zip_code
from {{ ref('stores') }}
