from django import template

register = template.Library()


@register.filter(name='get_sub')
def get_sub(first, second):
    return first - second
