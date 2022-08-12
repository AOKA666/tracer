from django import template

register = template.Library()


@register.simple_tag
def render_query_param(conditions):
    # conditions: {'status__in':[3,4], 'priority_in':[1,2]}
    query_param = ""
    filter_name = ["status__in", "issue_type__in", "priority__in", "assign__in", "attention__in"]
    for name in filter_name:
        if name in conditions:
            for value in conditions[name]:
                query_param += '{}={}&'.format(name[:-4], value)
    return query_param