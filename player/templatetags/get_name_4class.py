from django import template

register = template.Library()


@register.filter(name='get_name_4class')
def get_name_4class(value):
    return value.__name__
