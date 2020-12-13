from django import template

register = template.Library()


@register.filter(name='dict_key')
def key(d, key_name):
    return d[key_name]
