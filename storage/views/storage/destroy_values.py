from math import ceil

from player.player import Player
from storage.models.storage import Storage
from storage.models.transport import Transport
from storage.models.stock import Stock
from storage.models.destroy import Destroy

# Начисление товаров на целевой Склад
# входные данные:
# dest     - целевой склад
# values   - формат данных JSON из запроса
def destroy_values(player, values):

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

    # список записей на обновление
    stocks_mod = []
    # список айди записей на обновление
    stocks_mod_pk = []
    # список записей логов на обновление
    destroy_mod = []

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

                # логируем уничтожение
                destroy_log = Destroy(player=player,
                                        storage_from=Storage.actual.get(pk=int(storage)),
                                        good=s_stock.good,
                                        count=int(values[storage][stock_pk])
                                        )
                destroy_mod.append(destroy_log)

    # для всех измененных запасов выполняем сохранение
    if stocks_mod:
        Stock.objects.bulk_update(
            stocks_mod,
            fields=['stock', ],
            batch_size=len(stocks_mod)
        )

    # для всех измененных логов выполняем сохранение
    if destroy_mod:
        Destroy.objects.bulk_create(
            destroy_mod
        )