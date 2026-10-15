select
    cast(customer_id as integer) as customer_id,
    {{ clean_string('first_name') }} as first_name,
    {{ clean_string('last_name') }} as last_name,
    {{ clean_string('phone') }} as phone,
    lower({{ clean_string('email') }}) as email,
    {{ clean_string('street') }} as street,
    {{ clean_string('city') }} as city,
    {{ clean_string('state') }} as state,
    {{ clean_string('zip_code') }} as zip_code
from {{ ref('customers') }}
