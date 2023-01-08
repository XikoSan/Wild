from django import template

register = template.Library()


@register.filter(name='get_n_chars')
def get_n_chars(obj, n):
    return obj[0:n]
