from player.player import Player
from storage.models.storage import Storage
from storage.models.transport import Transport
from storage.models.stock import Stock
from region.models.region import Region
from math import ceil
from region.building.infrastructure import Infrastructure

#
# входные данные:
# trans_mul- словарь множителей расстояния от склада до склада
# dest     - pk Склада - цели
# values   - формат данных JSON из запроса
# dest_region - вместо ID склада передаётся id региона

# выходные данные:
# price    - общая цена перевозки
# prices   - словарь: цель - стоимость
def get_transfer_price(trans_mul, dest, values, dest_region=False):
    price = 0
    prices = {}

    infr_mul = {}
    storages_pk_list = []

    for storage in values.keys():
        storages_pk_list.append(int(storage))

    # получаем регионы всех переданных складов
    storages = Storage.actual.only('region').filter(pk__in=storages_pk_list)

    for warehouse in storages:
        infr_mul[warehouse.pk] = Infrastructure.indexes[Infrastructure.get_stat(warehouse.region)[0]['top']]

    if dest_region:
        dest_region = Region.objects.get(pk=dest)

        dest = f'reg_{dest}'
        infr_mul[dest] = Infrastructure.indexes[Infrastructure.get_stat(dest_region)[0]['top']]

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
    stocks = Stock.objects.only('pk', 'good__volume').filter(pk__in=stocks_pk_list)

    # идем по всем складам
    for storage in values.keys():
        # если в текущем Складе есть ресурсы
        if len(values.get(storage)):
            prices[int(storage)] = 0
            # идем по списку запасов
            for stock_pk in values.get(storage):

                val = ceil( ceil(int(values[storage][stock_pk]) * stocks.get(pk=stock_pk).good.volume) * trans_mul[dest][int(storage)] * ( ( 100 - infr_mul[dest] - infr_mul[int(storage)] ) / 100 ) )
                prices[int(storage)] += val
                price += val

    return price, prices
