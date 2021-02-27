from player.player import Player
from storage.models.storage import Storage
from storage.models.transport import Transport
from math import ceil

# проверка наличия места для товаров на указанном Складе, перед начислением их туда
# входные данные:
# trans_mul- словарь множителей расстояния от склада до склада
# dest     - pk Склада - цели
# values   - формат данных JSON из запроса

# выходные данные:
# price    - цена перевозки
def get_transfer_price(trans_mul, dest, values):
    price = 0
    # идем по всем складам
    for storage in values.keys():
        # если в текущем Складе есть ресурсы
        if len(values.get(storage)):
            # идём по списку товаров
            for good in values.get(storage):
                # надо понять, к какой категории относится товар. Так что, придётся пройтись по циклу
                # "minerals" - "oils" - "materials" - "units"
                for cat in ["minerals", "oils", "materials", "units"]:
                    if good in getattr(Transport, cat):
                        price += ceil(int(values.get(storage).get(good)) * getattr(Transport, cat)[good]) * trans_mul[dest][int(storage)]

    return price
