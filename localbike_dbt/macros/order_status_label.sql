{# Status codes come from the source system, labels are not stored anywhere in the raw data. #}
{% macro order_status_label(column_name) -%}
    case {{ column_name }}
        when 1 then 'Pending'
        when 2 then 'Processing'
        when 3 then 'Rejected'
        when 4 then 'Completed'
    end
{%- endmacro %}
