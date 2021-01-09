from django import template
register=template.Library()

@register.filter(name='get_mul')
def get_mul(first, second):
    return first * second