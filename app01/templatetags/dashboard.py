from django import template

register = template.Library()

@register.simple_tag
def render_space(space):
    if space >= 1024 * 1024 * 1024:
        return "{:.2f}GB".format(space/(1024 * 1024 * 1024))
    elif space >= 1024 * 1024:
        return "{:.2f}MB".format(space/(1024 * 1024))
    elif space >= 1024:
        return "{:.2f}KB".format(space/1024)
    else:
        return "{}B".format(space)