from django import template

register = template.Library()


@register.simple_tag
def render_query_param(conditions):
    query_param = ""
    filter_name = ["status__in", "issue_type__in", "priority__in", "assign__in", "attention__in"]
    for name in filter_name:
        if name in conditions:
            query_param += '{}={}'.format(name[:-4], conditions[name])
    return query_param