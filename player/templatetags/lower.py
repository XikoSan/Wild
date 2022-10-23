from django import template

register = template.Library()


@register.filter(name='lower')
def lower(obj):
    return obj.lower()
