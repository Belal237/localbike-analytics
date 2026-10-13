select
  brand_id,
  brand_name
from {{ ref('brands') }}
