from django import template
from math import floor

register = template.Library()


@register.filter
def floor_val(value):
    return floor(value)
