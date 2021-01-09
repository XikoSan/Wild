from django import template

register = template.Library()


@register.filter(name='get_mod')
def get_mod(first, second):
    return first % second
