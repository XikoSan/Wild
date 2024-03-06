from django import template

register = template.Library()
from storage.models.good_lock import GoodLock

from storage.models.stock import Stock
from storage.models.good import Good

@register.inclusion_tag('storage/redesign/storage_blocks/has_storage.html')
def has_storage(storage, player):

    goods_dict = {}
    cap_dict = {}

    for good in Good.objects.all():

        if Stock.objects.filter(storage=storage, good=good, stock__gt=0).exists():

            stock = Stock.objects.get(storage=storage, good=good, stock__gt=0)

        else:
            stock = Stock(storage=storage, good=good, stock=0)

        if good.size in goods_dict:
            goods_dict[good.size].append(stock)
            cap_dict[good.size] += stock.stock
        else:
            goods_dict[good.size] = [stock, ]
            cap_dict[good.size] = stock.stock

                
    size_dict = {}
    for size in Good.sizeChoices:
        size_dict[size[0]] = size[1]

    size_locks = {}
    locks = {}
    for lock in GoodLock.objects.filter(lock_storage=storage, deleted=False):

        if lock.lock_good in locks.keys():
            locks[lock.lock_good] += lock.lock_count
        else:
            locks[lock.lock_good] = lock.lock_count

        # по размерам
        if lock.lock_good.size in size_locks.keys():
            size_locks[lock.lock_good.size] += lock.lock_count
        else:
            size_locks[lock.lock_good.size] = lock.lock_count

    return {
        'player': player,

        # склад
        'storage': storage,
        'locks': locks,
        'size_dict': size_dict,
        'size_locks': size_locks,

        'goods_dict': goods_dict,
        'cap_dict': cap_dict,
    }
