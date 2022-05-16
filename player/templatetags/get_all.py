from django import template

register = template.Library()


@register.filter(name='get_all')
def get_all(obj):
    return obj.all()
