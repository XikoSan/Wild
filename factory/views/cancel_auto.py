# coding=utf-8

from django.contrib.auth.decorators import login_required
from django.db import transaction

from player.decorators.player import check_player
from factory.models.auto_produce import AutoProduce
from player.player import Player
from wild_politics.settings import JResponse
from django.utils.translation import ugettext
from django.utils.translation import pgettext


# выкопать ресурсы по запросу игрока
@login_required(login_url='/')
@check_player
@transaction.atomic
def cancel_auto_produce(request):
    if request.method == "POST":

        player = Player.get_instance(account=request.user)

        if AutoProduce.objects.filter(player=player).exists():
            AutoProduce.objects.filter(player=player).delete()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    else:
        data = {
            'header': pgettext('mining', 'Ошибка при отмене'),
            'grey_btn': pgettext('core', 'Закрыть'),
            'response': pgettext('core', 'Ошибка типа запроса'),
        }
        return JResponse(data)
