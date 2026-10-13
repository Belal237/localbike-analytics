select
  store_id,
  store_name,
  city,
  state,
  zip_code,
  phone,
  email,
  street
from {{ ref('stg_stores') }}
