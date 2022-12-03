from django import template
from storage.models.storage import Storage
register = template.Library()


@register.simple_tag
def check_up_limit(storage, good, size):
    mul = 1

    if size == 'large':
        mul = 10000
    elif size == 'medium':
        mul = 1000
    elif size == 'small':
        mul = 100

    if getattr(storage, good + '_cap') / mul == 10:
        return True

    return False
