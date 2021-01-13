from django import template

register = template.Library()


@register.filter(name='get_sum')
def get_sum(first, second):
    return first + second
