from django import template

register = template.Library()
from player.views.multiple_sum import multiple_sum


@register.filter(name='get_mul_cash')
def get_mul_cash(sum):
    return multiple_sum(sum)
