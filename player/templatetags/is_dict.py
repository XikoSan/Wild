from django import template

register = template.Library()


@register.filter(name='is_dict')
def is_dict(obj):
    return type(obj) is dict
