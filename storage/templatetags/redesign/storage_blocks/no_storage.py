import math
from django import template

from region.views.distance_counting import distance_counting
from storage.models.storage import Storage
from storage.views.storage.get_transfer_price import get_transfer_price

register = template.Library()


@register.inclusion_tag('storage/redesign/storage_blocks/no_storage.html')
def no_storage(player):
    # словарь склад - признак наличия достаточного количества материалов
    materials_exists = {}
    # словарь склад - сумма доставки из региона его размещения до региона нахождения игрока
    delivery_sum = {}

    price_dict = {}
    trans_mul = {}
    trans_mul[0] = {}

    # считаем стоиомость создания нового Склада
    # она равна 500 * количество Складов сейчас
    material_cost = 500 * Storage.objects.filter(owner=player).count()

    # получаем Склады игрока
    storages = Storage.objects.filter(owner=player)

    # узнаем, есть ли на Складах достаточно материалов для создания нового Склада, а также считаем доставку
    for storage in storages:
        price_dict[storage.pk] = {}
        price_dict[storage.pk]['steel'] = price_dict[storage.pk]['aluminium'] = material_cost

        trans_mul[0][storage.pk] = math.ceil(distance_counting(player.region, storage.region) / 100)

        # в словарь попадает True или False
        materials_exists[storage] = getattr(storage, 'steel') >= material_cost \
                                    and getattr(storage, 'aluminium') >= material_cost

    price, prices = get_transfer_price(trans_mul, 0, price_dict)
    for source_storage_pk in prices:
        delivery_sum[storages.get(pk=source_storage_pk)] = prices[source_storage_pk]

    return {
        'player': player,
        'storages': storages,
        'material_cost': material_cost,

        'materials_exists': materials_exists,
        'delivery_sum': delivery_sum,
    }
