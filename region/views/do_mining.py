# coding=utf-8
# import operator
# from datetime import timedelta
# from django.conf import settings
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import transaction

from player.decorators.player import check_player
from player.logs.gold_log import GoldLog
from player.player import Player
# from django.contrib.auth.models import User
# from django.db.models import Q
from state.models.state import State
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
        gold_log = None

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

            # player.cash += count
            gold_log = GoldLog(player=player, gold=int(count / 10), activity_txt='mine')
            # mined_result['cash'] = count

            player.region.gold_has -= Decimal((count / 10) * 0.01)

        elif resource == 'oil':
            # если запасов ресурса недостаточно
            if int(player.region.oil_has * 100) < count / 10:
                data = {
                    # 'response': _('mul_ten_enrg_req'),
                    'response': 'Запасов нефти в регионе недостаточно для добычи',
                    'header': 'Ошибка добычи ресурсов',
                    'grey_btn': 'Закрыть',
                }
                return JResponse(data)
            # получаем запасы склада, с учетом блокировок
            goods = [player.region.oil_type]
            lock_storage = get_storage(storage, goods)
            # облагаем налогом добытую нефть
            total_oil = (count / 10) * 10
            taxed_oil = State.get_taxes(player.region, total_oil, 'oil', player.region.oil_type)

            # проверяем есть ли для него место на складе, с учетом блокировок
            if lock_storage.capacity_check(player.region.oil_type, taxed_oil):
                # начислить нефть
                mined_result[player.region.oil_type] = taxed_oil
                setattr(storage, player.region.oil_type,
                        getattr(storage, player.region.oil_type) + taxed_oil)
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
            if int(player.region.ore_has * 100) < count / 10:
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
                # облагаем налогом добытую руду
                total_ore = (count / 10) * getattr(player.region, mineral + '_proc')
                taxed_ore = State.get_taxes(player.region, total_ore, 'ore', mineral)

                # проверяем есть ли место на складе
                if lock_storage.capacity_check(mineral, taxed_ore):
                    # начислить минерал
                    mined_result[mineral] = taxed_ore
                    setattr(storage, mineral,
                            getattr(storage, mineral) + taxed_ore)
                else:
                    # если места нет или его меньше чем пак ресурсов, забиваем под крышку
                    if taxed_ore > 0:
                        mined_result[mineral] = getattr(storage, mineral + '_cap') - getattr(lock_storage, mineral)
                        # устанавливаем новое значение как остаток до полного склада с учетом блокировок + старое значение ресурса
                        setattr(storage, mineral,
                                getattr(storage, mineral + '_cap') - getattr(lock_storage, mineral) + getattr(storage,
                                                                                                              mineral))

            player.region.ore_has -= Decimal((count / 10) * 0.01)

        if mined_result:
            if resource != 'gold':
                player.energy_cons(count)
            else:
                player.energy -= count
                player.save()

            if gold_log:
                gold_log.save()

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
