from django import template

register = template.Library()


@register.filter(name='is_list')
def is_list(obj):
    return type(obj) is list
