select
    store_id,
    store_name,
    city,
    state,
    zip_code,
    street,
    phone,
    email
from {{ ref('stg_stores') }}
