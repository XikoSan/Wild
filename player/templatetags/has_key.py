from django import template

register = template.Library()


@register.filter(name='has_key')
def has_key(d, key_name):
    return key_name in d.keys()
