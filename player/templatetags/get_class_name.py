from django import template

register = template.Library()


@register.filter(name='get_class_name')
def get_class_name(value):
    return value.__class__.__name__
