from django import template
from django.utils.translation import get_language

register = template.Library()

@register.simple_tag
def get_custom_language_code():
    language_code = get_language()
    return 'en' if language_code not in ['ru', 'be', 'uk', 'hy'] else 'ru'
