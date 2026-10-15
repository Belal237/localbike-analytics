{# Same idea as dbt_utils.unique_combination_of_columns, kept local to avoid a package dependency. #}
{% test unique_combination(model, columns) %}

select {{ columns | join(', ') }}
from {{ model }}
group by {{ columns | join(', ') }}
having count(*) > 1

{% endtest %}
