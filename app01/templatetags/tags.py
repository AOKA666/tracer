from django import template
register = template.Library()


@register.simple_tag
def render_error(form, field_name):
    return '' if not form.errors.get(field_name) else form.errors.get(field_name)


# @register.inclusion_tag("app01/inclusion/tag.html")
# def fetch_project(request):
#     pass