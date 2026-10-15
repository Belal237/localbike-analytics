with products as (
    select * from {{ ref('stg_products') }}
),

brands as (
    select * from {{ ref('stg_brands') }}
),

categories as (
    select * from {{ ref('stg_categories') }}
)

select
    products.product_id,
    products.product_name,
    products.model_year,
    products.list_price,
    products.brand_id,
    brands.brand_name,
    products.category_id,
    categories.category_name
from products
left join brands
    on products.brand_id = brands.brand_id
left join categories
    on products.category_id = categories.category_id
