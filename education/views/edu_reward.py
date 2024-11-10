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
from player.logs.gold_log import GoldLog
from player.logs.cash_log import CashLog


def edu_skip(player, reward_dict):

    for edu_id in reward_dict.keys():

        reward_line = reward_dict[edu_id]

        if reward_line['type'] == 'cash':
            if CashLog.objects.filter(player=player, activity_txt=edu_id).exists():
                continue

        if reward_line['type'] == 'gold':
            if GoldLog.objects.filter(player=player, activity_txt=edu_id).exists():
                continue

        reward_sum = reward_line['value']

        if reward_line['type'] == 'cash':
            player.cash += reward_sum

            CashLog.create(player=player, cash=reward_sum, activity_txt=edu_id)

        if reward_line['type'] == 'gold':
            player.gold += reward_sum

            gold_log = GoldLog(player=player, gold=reward_sum, activity_txt=edu_id)
            gold_log.save()

    player.educated = True
    player.save()

    data = {
        'response': 'ok',
    }
    return JResponse(data)

# получние наградного золота
@login_required(login_url='/')
@check_player
def edu_reward(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)
        reward_sum = 0

        reward_dict = {
            'financing': {
                'type': 'cash',
                'value': 845,
            },
            'cash': {
                'type': 'cash',
                'value': 800,
            },
        }

        edu_id = request.POST.get('edu_id')

        if edu_id == 'edu_all':
            return edu_skip(player, reward_dict)

        if not edu_id in reward_dict.keys():
            data = {
                'response': pgettext('education', 'Неизвестный ключ награды'),
                'header': pgettext('education', 'Ошибка получения награды'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        reward_line = reward_dict[edu_id]

        if reward_line['type'] == 'cash':
            if CashLog.objects.filter(player=player, activity_txt=edu_id).exists():
                data = {
                    'response': pgettext('education', 'Данная награда уже забрана'),
                    'header': pgettext('education', 'Ошибка получения награды'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JResponse(data)

        if reward_line['type'] == 'gold':
            if GoldLog.objects.filter(player=player, activity_txt=edu_id).exists():
                data = {
                    'response': pgettext('education', 'Данная награда уже забрана'),
                    'header': pgettext('education', 'Ошибка получения награды'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JResponse(data)

        reward_sum = reward_line['value']

        if reward_line['type'] == 'cash':
            player.cash += reward_sum

            CashLog.create(player=player, cash=reward_sum, activity_txt=edu_id)

        if reward_line['type'] == 'gold':
            player.gold += reward_sum

            gold_log = GoldLog(player=player, gold=reward_sum, activity_txt=edu_id)
            gold_log.save()

        player.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка метода'),
            'header': pgettext('education', 'Ошибка получения награды'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
