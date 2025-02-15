from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player
from wild_politics.settings import JResponse


# расход энергии со склада на пополнения её у персонажа
@login_required(login_url='/')
@check_player
def expense_energy(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        # fingerprinting
        if request.POST.get('fprint'):
            player.fingerprint = request.POST.get('fprint')

        else:
            data = {
                'response': pgettext('expense_energy', 'Отсутствует обязательный аргумент запроса'),
                'header': pgettext('expense_energy', 'Пополнение энергии'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        # время сейчас
        cur_time = timezone.now()
        # время, когда можно перезаряжаться
        end_time = player.last_refill
        # если время подзарядки ещё не пришло
        if end_time > cur_time:
            data = {
                'response': pgettext('expense_energy', 'Десять минут ещё не прошло'),
                'header': pgettext('expense_energy', 'Пополнение энергии'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        else:
            # если у игрока достаточно энергетиков
            if player.bottles >= 100 - player.energy:
                # количество энергии, которое необходимо восполнить
                refill_value = 100 - player.energy
                if refill_value > 0:
                    player.bottles -= refill_value
                    player.energy += refill_value
                    player.last_refill = timezone.now() + timedelta(seconds=600)
                    player.save()
                    data = {
                        'response': 'ok',
                    }
                    return JResponse(data)
                else:
                    data = {
                        'response': pgettext('expense_energy', 'Пополнение энергии не требуется'),
                        'header': pgettext('expense_energy', 'Пополнение энергии'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                    }
                    return JResponse(data)
            else:
                data = {
                    'response': pgettext('expense_energy', 'Недостаточно Энергетиков. Создайте их в Хранилище Склада'),
                    'header': pgettext('expense_energy', 'Пополнение энергии'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('expense_energy', 'Пополнение энергии'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
