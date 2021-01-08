from django import template

register = template.Library()


@register.inclusion_tag('storage/storage_blocks/has_storage.html')
def has_storage(storage):

    return {
        # склад
        'storage': storage,
    }
