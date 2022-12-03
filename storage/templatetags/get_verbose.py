from django import template
from storage.models.storage import Storage
register = template.Library()


@register.filter(name='get_verbose')
def get_verbose(i_good):
    for type in Storage.types.keys():
        for good in getattr(Storage, type).keys():
            if good == i_good:
                return getattr(Storage, type)[good]

    return 'None'
