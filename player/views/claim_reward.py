from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from wild_politics.settings import JResponse
from player.logs.gold_log import GoldLog


def edu_skip(player, gold_dict):

    for edu_id in gold_dict.keys():

        edu_gold = 0

        if GoldLog.objects.filter(player=player, activity_txt=edu_id).exists():
            continue

        edu_gold = gold_dict[edu_id]

        player.gold += edu_gold

        gold_log = GoldLog(player=player, gold=edu_gold, activity_txt=edu_id)
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
def claim_reward(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)
        edu_gold = 0

        gold_dict = {
            'edu_01': 200,
            'edu_02': 200,
            'edu_03': 200,
            'edu_04': 200,
            'edu_05': 200,
        }

        edu_id = request.POST.get('edu_id')

        if edu_id == 'edu_00':
            return edu_skip(player, gold_dict)

        if GoldLog.objects.filter(player=player, activity_txt=edu_id).exists():
            data = {
                'response': 'already_claimed',
            }
            return JResponse(data)

        edu_gold = gold_dict[edu_id]

        player.gold += edu_gold
        player.save()

        gold_log = GoldLog(player=player, gold=edu_gold, activity_txt=edu_id)
        gold_log.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            # 'response': _('positive_enrg_req'),
            'response': _('Ошибка типа запроса'),
            'header': _('Пополнение энергии'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
