from django import template

register = template.Library()


@register.filter(name='get_key_list')
def get_key_list(d):
    return d.keys()
