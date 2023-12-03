import math
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect

from player.decorators.player import check_player
from player.logs.cash_log import CashLog
from player.player import Player
from region.views.distance_counting import distance_counting
from storage.models.storage import Storage
from storage.views.storage.get_transfer_price import get_transfer_price
from django.utils.translation import pgettext
from storage.models.stock import Stock
from storage.models.good import Good
from django.db.models import F

# переименование партии
@login_required(login_url='/')
@check_player
@transaction.atomic
def new_storage(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        price_dict = {}
        trans_mul = {}

        # находим Склад, с которого хотят списать материалы
        if not Storage.actual.filter(pk=int(request.POST.get('storage')), owner=player):
            data = {
                'header': pgettext('storage', 'Новый Склад'),
                'response': pgettext('storage', 'Не найден Склад списания материалов'),
                'grey_btn': pgettext('mining', 'Закрыть'),
            }
            return JsonResponse(data)

        paid_storage = Storage.actual.get(pk=int(request.POST.get('storage')))
        price_dict[paid_storage.pk] = {}
        trans_mul[0] = {}
        trans_mul[0][paid_storage.pk] = math.ceil(distance_counting(player.region, paid_storage.region) / 100)

        # стоиомость создания нового Склада
        material_cost = 500

        # проверяем, что в складе-источнике достаточно сырья
        aluminium = Good.objects.get(name_ru='Алюминий')
        steel = Good.objects.get(name_ru='Сталь')

        for material in [aluminium, steel]:
            # проверяем наличие Запаса
            if not Stock.objects.filter(storage=paid_storage, good=material, stock__gte=material_cost).exists():
                data = {
                    'header': pgettext('storage', 'Новый Склад'),
                    'response': pgettext('storage', 'Недостаточно ресурса: ' + material.name),
                    'grey_btn': pgettext('mining', 'Закрыть'),
                }
                return JsonResponse(data)

        # получаем объекты запасов
        aluminium_stock = Stock.objects.get(storage=paid_storage, good=aluminium)
        steel_stock = Stock.objects.get(storage=paid_storage, good=steel)

        # создаем словарь транспорта
        price_dict[paid_storage.pk][aluminium_stock.pk] = price_dict[paid_storage.pk][steel_stock.pk] = material_cost

        # списываем ресурсы
        for stock in [aluminium_stock, steel_stock]:
            setattr(stock, 'stock', getattr(stock, 'stock') - material_cost)

        price, prices = get_transfer_price(trans_mul, 0, price_dict)
        if price > player.cash:
            data = {
                'header': pgettext('storage', 'Новый Склад'),
                'response': pgettext('storage', 'Недостаточно денег на транспортировку'),
                'grey_btn': pgettext('mining', 'Закрыть'),
            }
            return JsonResponse(data)
        # логируем
        CashLog.create(player=player, cash=0 - price, activity_txt='n_str')

        aluminium_stock.save()
        steel_stock.save()

        player.cash -= price
        player.save()

        storage = Storage(owner=player, region=player.region)
        storage.save()
        data = {
            'response': 'ok',
        }
        return JsonResponse(data)

    # если страницу только грузят
    else:
        data = {
            'header': pgettext('storage', 'Передача денег'),
            'grey_btn': pgettext('mining', 'Закрыть'),
            'response': pgettext('mining', 'Ошибка метода'),
        }
        return JsonResponse(data)
