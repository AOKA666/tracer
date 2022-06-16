from django import template
register = template.Library()


@register.simple_tag
def render_error(form, field_name):
    return '' if not form.errors.get(field_name) else form.errors.get(field_name)