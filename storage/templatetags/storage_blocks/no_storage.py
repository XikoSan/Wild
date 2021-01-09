from django import template

from region.views.distance_counting import distance_counting
from storage.storage import Storage

register = template.Library()


@register.inclusion_tag('storage/storage_blocks/no_storage.html')
def no_storage(player):
    # словарь склад - признак наличия достаточного количества материалов
    materials_exists = {}
    # словарь склад - сумма доставки из региона его размещения до региона нахождения игрока
    delivery_sum = {}

    # считаем стоиомость создания нового Склада
    # она равна 500 * количество Складов сейчас
    material_cost = 500 * Storage.objects.filter(owner=player).count()

    # получаем Склады игрока
    storages = Storage.objects.filter(owner=player)

    # узнаем, есть ли на Складах достаточно материалов для создания нового Склада, а также считаем доставку
    for storage in storages:
        # в словарь попадает True или False
        materials_exists[storage] = getattr(storage, 'steel') >= material_cost \
                                    and getattr(storage, 'aluminium') >= material_cost

        delivery_sum[storage] = round(distance_counting(player.region, storage.region))

    return {
        # склад
        'storages': storages,
        'material_cost': material_cost,

        'materials_exists': materials_exists,
        'delivery_sum': delivery_sum,
    }
