from django import template

register = template.Library()


@register.filter(name='get_str')
def get_str(first):
    return str(first)
