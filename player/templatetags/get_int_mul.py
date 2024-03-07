from django import template
register=template.Library()

@register.filter(name='get_int_mul')
def get_int_mul(first, second):
    return int(first * second)