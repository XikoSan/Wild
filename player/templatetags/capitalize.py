from django import template

register = template.Library()


@register.filter(name='capitalize')
def capitalize(obj):
    return obj.capitalize()
