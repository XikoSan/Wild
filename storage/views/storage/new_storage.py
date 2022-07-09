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
        if not Storage.objects.filter(pk=int(request.POST.get('storage')), owner=player):
            data = {
                'header': 'Новый Склад',
                'response': 'Не найден Склад',
                'grey_btn': 'Закрыть',
            }
            return JsonResponse(data)

        paid_storage = Storage.objects.get(pk=int(request.POST.get('storage')))
        price_dict[paid_storage.pk] = {}
        trans_mul[0] = {}
        trans_mul[0][paid_storage.pk] = math.ceil(distance_counting(player.region, paid_storage.region) / 100)
        # считаем стоиомость создания нового Склада
        # она равна 500 * количество Складов сейчас
        material_cost = 500 * Storage.objects.filter(owner=player).count()
        price_dict[paid_storage.pk]['steel'] = price_dict[paid_storage.pk]['aluminium'] = material_cost
        # если ресурсов недостаточно
        if not (getattr(paid_storage, 'steel') >= material_cost \
                and getattr(paid_storage, 'aluminium') >= material_cost):
            data = {
                'header': 'Новый Склад',
                'response': 'Недостаточно ресурсов',
                'grey_btn': 'Закрыть',
            }
            return JsonResponse(data)

        # списываем ресурсы
        setattr(paid_storage, 'steel', getattr(paid_storage, 'steel') - material_cost)
        setattr(paid_storage, 'aluminium', getattr(paid_storage, 'aluminium') - material_cost)

        price, prices = get_transfer_price(trans_mul, 0, price_dict)
        if price > player.cash:
            data = {
                'header': 'Новый Склад',
                'response': 'Недостаточно денег на транспортировку',
                'grey_btn': 'Закрыть',
            }
            return JsonResponse(data)
        # логируем
        CashLog(player=player, cash=0 - price, activity_txt='n_str').save()

        paid_storage.save()

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
            'response': 'Ты уверен что тебе сюда, путник?',
        }
        return JsonResponse(data)
