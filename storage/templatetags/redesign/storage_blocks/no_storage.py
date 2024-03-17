import math
from django import template

from region.views.distance_counting import distance_counting
from storage.models.storage import Storage
from storage.views.storage.get_transfer_price import get_transfer_price
from storage.models.stock import Stock
from storage.models.good import Good
from django.db.models import F

register = template.Library()


@register.inclusion_tag('storage/redesign/storage_blocks/no_storage.html')
def no_storage(player):
    # словарь склад - признак наличия достаточного количества материалов
    materials_exists = {}
    # словарь склад - сумма доставки из региона его размещения до региона нахождения игрока
    delivery_sum = {}

    price_dict = {}
    trans_mul = {}
    trans_mul[player.region.pk] = {}

    # считаем стоиомость создания нового Склада
    # она равна 500 * количество Складов сейчас
    material_cost = 500

    # получаем Склады игрока
    storages = Storage.actual.filter(owner=player)

    # узнаем, есть ли на Складах достаточно материалов для создания нового Склада, а также считаем доставку
    for storage in storages:
        aluminium = Good.objects.get(name_ru='Алюминий')
        steel = Good.objects.get(name_ru='Сталь')

        for material in [aluminium, steel]:
            # проверяем наличие Запаса
            if not Stock.objects.filter(storage=storage, good=material, stock__gte=material_cost).exists():
                materials_exists[storage] = False
                break

        # если есть запись в словаре - значит, какого-то запаса нет
        if storage in materials_exists:
            continue
        # иначе - нашли запасы
        else:
            materials_exists[storage] = True

        aluminium_stock = Stock.objects.get(storage=storage, good=aluminium)
        steel_stock = Stock.objects.get(storage=storage, good=steel)

        price_dict[storage.pk] = {}
        price_dict[storage.pk][aluminium_stock.pk] = price_dict[storage.pk][steel_stock.pk] = material_cost

        trans_mul[0][storage.pk] = math.ceil(distance_counting(player.region, storage.region) / 100)

    price, prices = get_transfer_price(trans_mul, player.region.pk, price_dict, dest_region=True)
    for source_storage_pk in prices:
        delivery_sum[storages.get(pk=source_storage_pk)] = prices[source_storage_pk]

    return {
        'player': player,
        'storages': storages,
        'material_cost': material_cost,

        'materials_exists': materials_exists,
        'delivery_sum': delivery_sum,
    }
