from django import template

register = template.Library()


@register.filter(name='get_div')
def get_div(first, second):
    return first / second
