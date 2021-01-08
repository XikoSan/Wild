from django import template

register = template.Library()


@register.inclusion_tag('storage/storage_blocks/no_storage.html')
def no_storage():
    return
