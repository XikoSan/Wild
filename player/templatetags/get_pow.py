from django import template
register=template.Library()

@register.filter(name='get_pow')
def get_pow(first, second):
    return first ** second