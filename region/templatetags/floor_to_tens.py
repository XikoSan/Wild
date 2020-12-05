from django import template
from math import floor

register = template.Library()


@register.filter
def floor_to_tens(value):
    return floor(value / 10) * 10
