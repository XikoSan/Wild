from django import template

register = template.Library()


@register.filter(name='get_int')
def get_int(obj):
    return int(obj)
