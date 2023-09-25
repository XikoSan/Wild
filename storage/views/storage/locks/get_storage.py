import copy

from storage.models.good_lock import Storage, GoodLock
from storage.models.stock import Stock, Good
from django.db.models import Sum

# получение Склада с блокировками ресурсов, для вычисления доступного места
# входные данные:
# storage - Склада, который нужно обработать

# выходные данные:
# Склад, к которому применены блокировки
def get_storage(storage, resources):
    ret_storage = copy.deepcopy(storage)
    if resources:
        lock_result = GoodLock.actual.filter(lock_storage=ret_storage, lock_good__in=resources)
    else:
        lock_result = GoodLock.actual.filter(lock_storage=ret_storage)
    # по всем блокировкам этого склада
    for lock_line in lock_result.filter(lock_storage=ret_storage):
        setattr(ret_storage, getattr(lock_line, 'lock_good'),
                getattr(ret_storage, getattr(lock_line, 'lock_good')) + lock_line.lock_count)

    return ret_storage


# получение словаря Запасов с блокировками ресурсов, а также данных емкости по типоразмерам
# входные данные:
# storage - Склад, который нужно обработать

# выходные данные:
# словарь запасов: товар - запасы (с блокировками)
# словарь емкостей: типоразмер - занятое пространство
def get_stocks(storage, resources=None):

    ret_stocks = {}
    ret_st_stocks = {}

    if resources:
        # ресурсы, которые были выбраны
        selected_goods = Good.objects.filter(name_ru__in=resources)

        selected_sizes = []
        # узнаем каких типоразмеров ресурсы выгрузить помимо искомых,
        # чтобы получить информацию по заполнению хранилища
        for good in selected_goods:
            if not good.size in selected_sizes:
                selected_sizes.append(good.size)
        # получаем все товары указанных типоразмеров (включая искомые)
        goods = Good.objects.filter(size__in=selected_sizes)

    else:
        goods = Good.objects.all()

    # блокировки
    locks = GoodLock.actual.filter(lock_storage=storage, lock_good__in=goods)
    # ненулевые запасы
    stocks = Stock.objects.filter(storage=storage, stock__gt=0, good__in=goods)

    # создаем словари на выход
    for good in goods:
        # если есть ненулевые запасы в этом складе
        if stocks.filter(good=good).exists():

            if locks.filter(lock_good=good).aggregate(Sum('lock_count'))['lock_count__sum']:
                sum = stocks.get(good=good).stock + locks.filter(lock_good=good).aggregate(Sum('lock_count'))['lock_count__sum']
            else:
                sum = stocks.get(good=good).stock

            # по ресурсу (только искомые)
            if good.name in resources:
                ret_stocks[good] = sum

            # по типоразмеру (все одного ТР)
            if not good.size in ret_st_stocks:
                ret_st_stocks[good.size] = sum
            else:
                ret_st_stocks[good.size] += sum

        else:
            # по ресурсу (только искомые)
            ret_stocks[good] = 0

            # по типоразмеру (все одного ТР)
            if not good.size in ret_st_stocks:
                ret_st_stocks[good.size] = 0


    return ret_stocks, ret_st_stocks
