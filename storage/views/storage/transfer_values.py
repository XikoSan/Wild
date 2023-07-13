from math import ceil

from player.player import Player
from storage.models.storage import Storage
from storage.models.transport import Transport
from storage.models.stock import Stock

# Начисление товаров на целевой Склад
# входные данные:
# dest     - целевой склад
# values   - формат данных JSON из запроса
def transfer_values(dest, values, prices):

    # список айдишников запасов, которые будем обрабатывать
    stocks_pk_list = []

    # идем по всем складам
    for storage in values.keys():
        # если в текущем Складе есть ресурсы
        if len(values.get(storage)):
            # идем по списку запасов
            for stock_pk in values.get(storage):
                # собираем айдишники запасов
                stocks_pk_list.append(stock_pk)

    # получаем все запасы, которые требуются
    stocks = Stock.objects.select_for_update().filter(pk__in=stocks_pk_list)

    # список товаров, которые используются в передавамых запасах
    goods_list = []

    for stock in stocks:
        if not stock.good in goods_list:
            goods_list.append(stock.good)

    # получаем Запасы с передаваемыми товарами в целевом складе
    dest_stocks = Stock.objects.select_for_update().filter(storage=dest, good__in=goods_list)

    # список Запасов, которые были созданы только что
    new_stocks_dict = {}

    # если такого запаса нет - создаем
    for good in goods_list:
        if not dest_stocks.filter(good=good).exists():
            stock, created = Stock.objects.get_or_create(storage=dest,
                                                         good=good
                                                         )
            new_stocks_dict[good] = stock

    # список записей на обновление
    stocks_mod = []
    # список айди записей на обновление
    stocks_mod_pk = []

    # идем по всем складам
    for storage in values.keys():
        # если в текущем Складе есть ресурсы
        if len(values.get(storage)):
            # идем по списку запасов
            for stock_pk in values.get(storage):
                # списываем запас из источника
                s_stock = stocks.get(pk=stock_pk)

                s_stock.stock -= int(values[storage][stock_pk])
                stocks_mod.append(s_stock)
                stocks_mod_pk.append(s_stock.pk)

                # логируем списание
                transport, created = Transport.objects.get_or_create(player=dest.owner,
                                                                 storage_from=Storage.actual.get(pk=int(storage)),
                                                                 storage_to=dest,
                                                                 good=s_stock.good,
                                                                 count=0-int(values[storage][stock_pk]),
                                                                 total_vol=ceil(int(values[storage][stock_pk]) * s_stock.good.volume),
                                                                 )
                # начисляем в целевой склад
                if dest_stocks.filter(good=s_stock.good).exists():
                    dest_stock = dest_stocks.get(good=s_stock.good)

                else:
                    dest_stock = new_stocks_dict[s_stock.good]

                # если запись уже модифицировали - берем измененную
                if dest_stock.pk in stocks_mod_pk:
                    dest_stock = stocks_mod.pop( stocks_mod_pk.index(dest_stock.pk) )
                    stocks_mod_pk.pop(stocks_mod_pk.index(dest_stock.pk))

                dest_stock.stock += int(values[storage][stock_pk])
                stocks_mod.append(dest_stock)
                stocks_mod_pk.append(dest_stock.pk)

    # для всех измененных запасов выполняем сохранение
    if stocks_mod:
        Stock.objects.bulk_update(
            stocks_mod,
            fields=['stock', ],
            batch_size=len(stocks_mod)
        )