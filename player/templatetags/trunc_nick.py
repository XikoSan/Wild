from django import template
from math import floor

register = template.Library()


@register.filter
def trunc_nick(value):
    if ' ' not in value:
        return value[:10] + '...' if len(value) > 10 else value
    return value
