from django import template

register = template.Library()
from storage.models.good_lock import GoodLock

@register.inclusion_tag('storage/storage_blocks/has_storage.html')
def has_storage(storage):
    locks = {}
    for lock in GoodLock.objects.filter(lock_storage=storage):
        if lock.lock_good in locks.keys():
            locks[lock.lock_good] += lock.lock_count
        else:
            locks[lock.lock_good] = lock.lock_count

    return {
        # склад
        'storage': storage,
        'locks': locks,
    }
