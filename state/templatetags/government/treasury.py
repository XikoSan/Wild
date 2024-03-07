from django import template

register = template.Library()
from state.models.treasury import Treasury
from storage.models.storage import Storage
from state.models.treasury_lock import TreasuryLock
from storage.models.stock import Stock
from storage.models.good import Good
from state.models.treasury_stock import TreasuryStock

@register.inclusion_tag('state/gov/treasury.html')
def treasury(state):
    treasury = None

    type_dict = {}
    for type in Good.typeChoices:
        type_dict[type[0]] = type[1]

    goods_dict = {}
    locks = {}

    if Treasury.objects.filter(state=state).exists():
        # находим казну государства
        treasury = Treasury.get_instance(state=state)

        for good in Good.objects.all():
            if TreasuryStock.objects.filter(treasury=treasury, good=good, stock__gt=0).exists():
                stock = TreasuryStock.objects.get(treasury=treasury, good=good, stock__gt=0)

            else:
                stock = TreasuryStock(treasury=treasury, good=good, stock=0)

            if good.type in goods_dict:
                goods_dict[good.type].append(stock)

            else:
                goods_dict[good.type] = [stock, ]

        for lock in TreasuryLock.actual.filter(lock_treasury=treasury):
            if lock.cash:
                if 'cash' in locks.keys():
                    locks['cash'] += lock.lock_count
                else:
                    locks['cash'] = lock.lock_count

            else:
                if lock.lock_good in locks.keys():
                    locks[lock.lock_good] += lock.lock_count
                else:
                    locks[lock.lock_good] = lock.lock_count

    return {
        # казна
        'treasury': treasury,
        # класс Товара
        'good_cl': Good,
        # блокировки
        'locks': locks,
        # словарь типов товаров
        'type_dict': type_dict,
        # запасы
        'goods_dict': goods_dict,
    }
