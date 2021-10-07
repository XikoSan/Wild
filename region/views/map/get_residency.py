# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone

from player.decorators.player import check_player
from player.player import Player
from wild_politics.settings import JResponse


# получить прописку
@login_required(login_url='/')
@check_player
@transaction.atomic
def get_residency(request):
    if request.method == "POST":

        player = Player.objects.select_for_update().get(account=request.user)

        if player.destination:
            data = {
                # 'response': _('wait_flight_end'),
                'response': 'Дождитесь конца полёта',
                'header': 'Ошибка добычи ресурсов',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        player.residency = player.region
        player.residency_date = timezone.now()
        player.save()

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
