from django import template

register = template.Library()


@register.filter(name='check_object')
def check_object(obj):
    return not obj is None
