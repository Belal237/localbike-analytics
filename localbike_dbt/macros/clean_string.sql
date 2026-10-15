{#
    The raw exports write missing values as the literal text 'NULL'
    (customers.phone for example). This turns them, and empty strings, into real nulls.
#}
{% macro clean_string(column_name) -%}
    nullif(nullif(trim(cast({{ column_name }} as {{ dbt.type_string() }})), 'NULL'), '')
{%- endmacro %}
