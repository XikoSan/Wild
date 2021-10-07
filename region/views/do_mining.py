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
from player.logs.cash_log import CashLog
from player.player import Player
from storage.models.storage import Storage
from storage.views.storage.locks.get_storage import get_storage
# from django.http import JResponse, HttpResponse
from wild_politics.settings import JResponse


# главная страница
@login_required(login_url='/')
@check_player
@transaction.atomic
def do_mining(request):
    if request.method == "POST":

        player = Player.objects.get(account=request.user)
        cash_log = None

        if player.destination:
            data = {
                # 'response': _('wait_flight_end'),
                'response': 'Дождитесь конца полёта',
                'header': 'Ошибка добычи ресурсов',
                'grey_btn': 'Закрыть',
            }
            # return JResponse(data)
            return JResponse(data)
            # return HttpResponse('Дождитесь конца полёта')

        resource = request.POST.get('resource')

        if not Storage.objects.filter(owner=player, region=player.region).exists() \
                and resource != 'gold':
            data = {
                'response': 'У вас нет склада в этом регионе',
                'header': 'Ошибка добычи ресурсов',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        # узнаем сколько он хочет потратить энергии
        count = request.POST.get('energy', '')

        if not count.isdigit():
            data = {
                'header': 'Ошибка при создании',
                'grey_btn': 'Закрыть',
                'response': 'Количество энергии - не число',
            }
            return JResponse(data)

        count = int(count)

        # Количество Энергии должно быть положительным
        if count <= 0:
            data = {
                # 'response': _('positive_enrg_req'),
                'response': 'Количество Энергии должно быть положительным',
                'header': 'Ошибка добычи ресурсов',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)
        # Количество Энергии должно быть кратно десяти
        if count % 10 != 0:
            data = {
                # 'response': _('mul_ten_enrg_req'),
                'response': 'Количество Энергии должно быть кратно десяти',
                'header': 'Ошибка добычи ресурсов',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        if count > player.energy:
            data = {
                # 'response': _('mul_ten_enrg_req'),
                'response': 'Недостаточно энергии',
                'header': 'Ошибка добычи ресурсов',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        mined_result = {}

        if resource != 'gold':
            storage = Storage.objects.get(owner=player, region=player.region)

        if resource == 'gold':
            # если запасов ресурса недостаточно
            if player.region.gold_has < Decimal((count / 10) * 0.01):
                data = {
                    # 'response': _('mul_ten_enrg_req'),
                    'response': 'Запасов золота в регионе недостаточно для добычи',
                    'header': 'Ошибка добычи ресурсов',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)

            player.gold += count / 10
            mined_result['gold'] = int(count / 10)

            player.cash += count
            cash_log = CashLog(player=player, cash=count, activity_txt='mine')
            mined_result['cash'] = count

            player.region.gold_has -= Decimal((count / 10) * 0.01)

        elif resource == 'oil':
            # если запасов ресурса недостаточно
            if player.region.oil_has < Decimal((count / 10) * 0.01):
                data = {
                    # 'response': _('mul_ten_enrg_req'),
                    'response': 'Запасов нефти в регионе недостаточно для добычи',
                    'header': 'Ошибка добычи ресурсов',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)
            # получаем запасы склада, с учетом блокировок
            goods = []
            goods.append(player.region.oil_type)
            lock_storage = get_storage(storage, goods)
            # узнаём тип нефти, добываемый в регионе
            # и проверяем есть ли для него место на складе, с учетом блокировок
            if lock_storage.capacity_check(player.region.oil_type, (count / 10) * 10):
                # начислить нефть
                mined_result[player.region.oil_type] = (count / 10) * 10
                setattr(storage, player.region.oil_type,
                        getattr(storage, player.region.oil_type) + (count / 10) * 10)
            else:
                # если места нет или его меньше чем пак ресурсов, забиваем под крышку
                mined_result[player.region.oil_type] = getattr(storage, player.region.oil_type + '_cap') - getattr(
                    lock_storage, player.region.oil_type)
                # устанавливаем новое значение как остаток до полного склада с учетом блокировок + старое значение ресурса
                setattr(storage, player.region.oil_type,
                        (getattr(storage, player.region.oil_type + '_cap') - getattr(lock_storage,
                                                                                     player.region.oil_type)) +
                        getattr(storage, player.region.oil_type)
                        )

            player.region.oil_has -= Decimal((count / 10) * 0.01)

        elif resource == 'ore':
            # если запасов ресурса недостаточноы
            if player.region.ore_has < Decimal((count / 10) * 0.01):
                data = {
                    # 'response': _('mul_ten_enrg_req'),
                    'response': 'Запасов руды в регионе недостаточно для добычи',
                    'header': 'Ошибка добычи ресурсов',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)
            goods = []
            for key in storage.minerals.keys():
                goods.append(key)
            lock_storage = get_storage(storage, goods)
            for mineral in storage.minerals.keys():
                # проверяем есть ли место на складе
                if lock_storage.capacity_check(mineral, (count / 10) * getattr(player.region, mineral + '_proc')):
                    # начислить минерал
                    mined_result[mineral] = (count / 10) * getattr(player.region, mineral + '_proc')
                    setattr(storage, mineral,
                            getattr(storage, mineral) + (count / 10) * getattr(player.region, mineral + '_proc'))
                else:
                    # если места нет или его меньше чем пак ресурсов, забиваем под крышку
                    if (count / 10) * getattr(player.region, mineral + '_proc') > 0:
                        mined_result[mineral] = getattr(storage, mineral + '_cap') - getattr(lock_storage, mineral)
                        # устанавливаем новое значение как остаток до полного склада с учетом блокировок + старое значение ресурса
                        setattr(storage, mineral,
                                getattr(storage, mineral + '_cap') - getattr(lock_storage, mineral) + getattr(storage,
                                                                                                              mineral))

            player.region.ore_has -= Decimal((count / 10) * 0.01)

        if mined_result:
            player.energy -= count
            player.save()

            if cash_log:
                cash_log.save()

            player.region.save()

            if resource != 'gold':
                storage.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    else:
        data = {
            'header': 'Ошибка при создании',
            'grey_btn': 'Закрыть',
            'response': 'Ты уверен что тебе сюда, путник?',
        }
        return JResponse(data)
