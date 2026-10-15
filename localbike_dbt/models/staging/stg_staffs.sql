select
    cast(staff_id as integer) as staff_id,
    {{ clean_string('first_name') }} as first_name,
    {{ clean_string('last_name') }} as last_name,
    lower({{ clean_string('email') }}) as email,
    {{ clean_string('phone') }} as phone,
    cast(active as integer) = 1 as is_active,
    cast(store_id as integer) as store_id,
    cast(manager_id as integer) as manager_id
from {{ ref('staffs') }}
