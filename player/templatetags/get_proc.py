from django import template

register = template.Library()


@register.filter(name='get_proc')
def get_proc(full, val):
    return (val/full)*100
