import math
import json
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
from storage.templatetags.get_verbose import get_verbose
from storage.templatetags.check_up_limit import check_up_limit

from storage.models.stock import Stock, Good


# переименование партии
@login_required(login_url='/')
@check_player
@transaction.atomic
def upgrade_storage(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        alu_stock = None
        steel_stock = None

        # если у игрока в этом регионе есть Склад
        if not Storage.actual.filter(owner=player, region=player.region).exists():
            data = {
                'header': pgettext('storage_upgrade', 'Улучшение Склада'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('storage', 'В этом регионе нет Склада'),
            }
            return JsonResponse(data)

        storage = Storage.actual.get(owner=player, region=player.region)

        if storage.level >= 5  and ( storage.level - 4 ) * 25 > player.knowledge:
            data = {
                'header': pgettext('storage_upgrade', 'Улучшение Склада'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('storage_upgrade', "Требуется Интеллект: %(int_require)s") % { "int_require": ( storage.level - 4 ) * 25 },
            }
            return JsonResponse(data)

        for material in ['Алюминий', 'Сталь']:
            if Good.objects.filter(name_ru=material).exists():

                mat = Good.objects.get(name_ru=material)

                if not Stock.objects.filter(storage=storage, good=mat, stock__gte=500).exists():
                    data = {
                        'header': pgettext('storage_upgrade', 'Улучшение Склада'),
                        'grey_btn': pgettext('mining', 'Закрыть'),
                        'response': pgettext('storage_upgrade', 'Недостаточно материала: ') + str(mat.name),
                    }
                    return JsonResponse(data)

                else:
                    if material == 'Алюминий':
                        alu_stock = Stock.objects.get(storage=storage, good=mat)
                    else:
                        steel_stock = Stock.objects.get(storage=storage, good=mat)


        storage.level += 1
        storage.large_cap += 120000
        storage.medium_cap += 20000
        storage.small_cap += 2000

        alu_stock.stock -= 500
        alu_stock.save()

        steel_stock.stock -= 500
        steel_stock.save()

        storage.save()

        data = {
            'response': 'ok',
        }
        return JsonResponse(data)

    # если страницу только грузят
    else:
        data = {
            'header': pgettext('storage_upgrade', 'Улучшение Склада'),
            'grey_btn': pgettext('mining', 'Закрыть'),
            'response': pgettext('mining', 'Ошибка метода'),
        }
        return JsonResponse(data)
