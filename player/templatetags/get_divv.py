from django import template

register = template.Library()


@register.filter(name='get_divv')
def get_divv(first, second):
    return first // second
