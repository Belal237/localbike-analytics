with staffs as (
    select * from {{ ref('stg_staffs') }}
)

select
    staffs.staff_id,
    staffs.first_name || ' ' || staffs.last_name as staff_name,
    staffs.email,
    staffs.is_active,
    staffs.store_id,
    stores.store_name,
    staffs.manager_id,
    managers.first_name || ' ' || managers.last_name as manager_name
from staffs
left join {{ ref('stg_stores') }} as stores
    on staffs.store_id = stores.store_id
left join staffs as managers
    on staffs.manager_id = managers.staff_id
