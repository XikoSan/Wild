import json
import math
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect

from player.decorators.player import check_player
from player.player import Player
from region.views.distance_counting import distance_counting
from storage.models.destroy import Destroy
from storage.models.storage import Storage
from storage.views.storage.check_cap_exists import check_cap_exists
from storage.views.storage.check_goods_exists import check_goods_exists
from storage.views.storage.get_transfer_price import get_transfer_price
from storage.views.storage.transfer_values import transfer_values
from django.utils.translation import pgettext


# переименование партии
@login_required(login_url='/')
@check_player
@transaction.atomic
def storage_move(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        # получаем целевой склад
        dest_pk = request.POST.get('storage')

        if dest_pk == 'null':
            data = {
                'header': pgettext('assets', 'Перемещение Склада'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('assets', 'Склад не заполнен'),
            }
            return JsonResponse(data)

        # проверяем, есть ли целевой склад среди складов игрока
        if not Storage.actual.filter(owner=player, pk=int(dest_pk)):
            data = {
                'header': pgettext('assets', 'Перемещение Склада'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('assets', 'Указанный Склад вам не принадлежит'),
            }
            return JsonResponse(data)

        storage = Storage.actual.select_for_update().get(pk=int(dest_pk))

        if storage.region == player.region:
            data = {
                'header': pgettext('assets', 'Перемещение Склада'),
                'grey_btn': pgettext('mining', 'Закрыть'),
                'response': pgettext('assets', 'Указанный Склад уже в текущем регионе'),
            }
            return JsonResponse(data)

        storage.region = player.region
        storage.was_moved = True

        storage.save()

        data = {
            'response': 'ok',
        }
        return JsonResponse(data)

    # если страницу только грузят
    else:
        data = {
            'header': pgettext('assets', 'Перемещение Склада'),
            'grey_btn': pgettext('mining', 'Закрыть'),
            'response': pgettext('mining', 'Ошибка метода'),
        }
        return JsonResponse(data)
