# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone

from player.decorators.player import check_player
from player.logs.auto_mining import AutoMining
from player.player import Player
from storage.models.storage import Storage
from wild_politics.settings import JResponse


# выкопать ресурсы по запросу игрока
@login_required(login_url='/')
@check_player
@transaction.atomic
def start_auto(request):
    if request.method == "POST":

        player = Player.get_instance(account=request.user)

        if player.destination:
            data = {
                # 'response': _('wait_flight_end'),
                'response': 'Дождитесь конца полёта',
                'header': 'Ошибка автоматической добычи ресурсов',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        if player.premium < timezone.now():
            data = {
                # 'response': _('wait_flight_end'),
                'response': 'Премиум-аккаунт не активен. Продлите его',
                'header': 'Ошибка автоматической добычи ресурсов',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        resource = request.POST.get('resource')

        from player.logs.print_log import log
        log(resource)

        if not resource in ['gold', 'oil', 'ore']:
            data = {
                # 'response': _('wait_flight_end'),
                'response': 'Неизвестный тип ресурса',
                'header': 'Ошибка автоматической добычи ресурсов',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        # если у игрока нет Склада в этом регионе, то Нефть и Руду собирать он не сможет
        if resource in ['ore', 'oil'] and not Storage.actual.filter(owner=player, region=player.region).exists():
            data = {
                # 'response': _('wait_flight_end'),
                'response': 'У вас нет склада в этом регионе',
                'header': 'Ошибка автоматической добычи ресурсов',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        if AutoMining.objects.filter(player=player).exists():
            AutoMining.objects.filter(player=player).delete()

        auto = AutoMining(
            player=player,
            resource=resource,
        )

        auto.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    else:
        data = {
            'header': 'Ошибка автоматической добычи ресурсов',
            'grey_btn': 'Закрыть',
            'response': 'Ты уверен что тебе сюда, путник?',
        }
        return JResponse(data)
