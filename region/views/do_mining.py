# coding=utf-8
# import operator
# from datetime import timedelta
# from django.conf import settings
import random
import time
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
# from django.contrib.auth.models import User
# from django.db.models import Q
from django.shortcuts import redirect, render

from player.decorators.player import check_player
from player.player import Player
from storage.storage import Storage
# from django.http import JResponse, HttpResponse
from wild_politics.settings import JResponse


# главная страница
@login_required(login_url='/')
@check_player
@transaction.atomic
def do_mining(request):
    if request.method == "POST":

        player = Player.objects.get(account=request.user)

        if player.destination:
            data = {
                # 'responce': _('wait_flight_end'),
                'response': 'Дождитесь конца полёта',
            }
            # return JResponse(data)
            return JResponse(data)
            # return HttpResponse('Дождитесь конца полёта')

        if not Storage.objects.filter(owner=player, region=player.region).exists():
            data = {
                'response': 'У вас нет склада в этом регионе',
            }
            return JResponse(data)

        # узнаем сколько он хочет потратить энергии
        count = int(request.POST.get('energy', ''))
        # Количество Энергии должно быть положительным
        if count <= 0:
            data = {
                # 'response': _('positive_enrg_req'),
                'response': 'Количество Энергии должно быть положительным',
            }
            return JResponse(data)
        # Количество Энергии должно быть кратно десяти
        if count % 10 != 0:
            data = {
                # 'responce': _('mul_ten_enrg_req'),
                'response': 'Количество Энергии должно быть кратно десяти',
            }
            return JResponse(data)

        mined_result = {}
        storage = Storage.objects.get(owner=player, region=player.region)

        resource = request.POST.get('resource')

        if resource == 'oil':
            # если запасов ресурса недостаточно
            if player.region.oil_has < Decimal((count / 10) * 0.01):
                data = {
                    # 'responce': _('mul_ten_enrg_req'),
                    'response': 'Запасов нефти в регионе недостаточно для добычи',
                }
                return JResponse(data)
            # узнаём тип нефти, добываемый в регионе
            # и проверяем есть ли для него место на складе
            if storage.capacity_check(player.region.oil_type, (count / 10) * 10):
                # начислить нефть
                mined_result[player.region.oil_type] = (count / 10) * 10
                setattr(storage, player.region.oil_type,
                        getattr(storage, player.region.oil_type) + (count / 10) * 10)
            else:
                # если места нет или его меньше чем пак ресурсов, забиваем под крышку
                mined_result[player.region.oil_type] = getattr(storage, player.region.oil_type + '_cap') - getattr(
                    storage, player.region.oil_type)
                setattr(storage, player.region.oil_type, getattr(storage, player.region.oil_type + '_cap'))

            player.region.oil_has -= Decimal((count / 10) * 0.01)

        elif resource == 'ore':
            # если запасов ресурса недостаточно
            if player.region.ore_has < Decimal((count / 10) * 0.01):
                data = {
                    # 'responce': _('mul_ten_enrg_req'),
                    'response': 'Запасов руды в регионе недостаточно для добычи',
                }
                return JResponse(data)
            for mineral in storage.minerals.keys():
                # проверяем есть ли место на складе
                if storage.capacity_check(mineral, (count / 10) * getattr(player.region, mineral + '_proc')):
                    # начислить минерал
                    mined_result[mineral] = (count / 10) * getattr(player.region, mineral + '_proc')
                    setattr(storage, mineral,
                            getattr(storage, mineral) + (count / 10) * getattr(player.region, mineral + '_proc'))
                else:
                    # если места нет или его меньше чем пак ресурсов, забиваем под крышку
                    if (count / 10) * getattr(player.region, mineral + '_proc') > 0:
                        mined_result[mineral] = getattr(storage, mineral + '_cap') - getattr(storage, mineral)
                        setattr(storage, mineral, getattr(storage, mineral + '_cap'))

            player.region.ore_has -= Decimal((count / 10) * 0.01)

        player.energy -= count
        player.save()

        player.region.save()

        storage.save()

        data = {
            'response': 'ok',
            'mined': mined_result,
        }
        return JResponse(data)

    else:
        pass
