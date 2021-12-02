from django import template

register = template.Library()


@register.filter(name='get_diff')
def get_diff(first, second):
    return first - second
