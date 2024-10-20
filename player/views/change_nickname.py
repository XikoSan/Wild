from django.contrib.auth.decorators import login_required
from django.db import transaction

from player.decorators.player import check_player
from player.logs.gold_log import GoldLog
from player.player import Player
from wild_politics.settings import JResponse
from django.utils.translation import pgettext


# расход энергии со склада на пополнения её у персонажа
@login_required(login_url='/')
@check_player
@transaction.atomic
def change_nickname(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        if player.gold < 50:
            data = {
                'response': pgettext('change_nickname', 'Недостаточно золота, необходимо: 50'),
                'header': pgettext('change_nickname', 'Смена никнейма'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        nickname = request.POST.get('nickname')

        if nickname == '':
            data = {
                'response': pgettext('change_nickname', 'Никнейм не может быть пустым'),
                'header': pgettext('change_nickname', 'Смена никнейма'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        if nickname == player.nickname:
            data = {
                'response': pgettext('change_nickname', 'Никнейм не изменился'),
                'header': pgettext('change_nickname', 'Смена никнейма'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        player.nickname = nickname[:30]
        player.gold -= 50

        gold_log = GoldLog(player=player, gold=-50, activity_txt='nick')
        gold_log.save()

        player.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)


    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('change_nickname', 'Смена никнейма'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
