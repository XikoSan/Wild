from player.player import Player
from storage.models.storage import Storage
from storage.models.transport import Transport
from math import ceil

#
# входные данные:
# trans_mul- словарь множителей расстояния от склада до склада
# dest     - pk Склада - цели
# values   - формат данных JSON из запроса

# выходные данные:
# price    - общая цена перевозки
# prices   - словарь: цель - стоимость
def get_transfer_price(trans_mul, dest, values):
    price = 0
    prices = {}
    # идем по всем складам
    for storage in values.keys():
        # если в текущем Складе есть ресурсы
        if len(values.get(storage)):
            prices[int(storage)] = 0
            # идём по списку товаров
            for good in values.get(storage):
                # проверка, существует ли такой ресурс вообще
                if not hasattr(Storage, good):
                    continue
                # надо понять, к какой категории относится товар. Так что, придётся пройтись по циклу
                # "minerals" - "oils" - "materials" - "units"
                for cat in Storage.types.keys():
                    if good in getattr(Transport, cat):
                        prices[int(storage)] += ceil(int(values.get(storage).get(good)) * getattr(Transport, cat)[good]) * trans_mul[dest][int(storage)]
                        price += ceil(int(values.get(storage).get(good)) * getattr(Transport, cat)[good]) * trans_mul[dest][int(storage)]

    return price, prices
