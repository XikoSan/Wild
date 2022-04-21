# coding=utf-8

from django.contrib.auth.decorators import login_required
from django.db import transaction

from player.decorators.player import check_player
from player.logs.auto_mining import AutoMining
from player.player import Player
from wild_politics.settings import JResponse


# выкопать ресурсы по запросу игрока
@login_required(login_url='/')
@check_player
@transaction.atomic
def cancel_auto(request):
    if request.method == "POST":

        player = Player.get_instance(account=request.user)

        if AutoMining.objects.filter(player=player).exists():
            AutoMining.objects.filter(player=player).delete()

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
