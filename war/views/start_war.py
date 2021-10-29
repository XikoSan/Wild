import datetime
import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from player.decorators.player import check_player
from player.player import Player
from war.models.wars.event_war import EventWar
from war.models.wars.war_side import WarSide
from wild_politics.settings import JResponse


# запуск войны в текущем регионе
@login_required(login_url='/')
@check_player
@transaction.atomic
def start_war(request):
    if request.method == "POST":
        if not request.user.is_superuser:
            data = {
                'response': 'Вы не имеете требуемых полномочий',
            }
            return JResponse(data)

        # получаем персонажа
        player = Player.objects.select_for_update().get(account=request.user)

        # создаем новую войну
        war = EventWar(
            running=True,
            round=0,
            start_time=timezone.now(),
            agr_region=player.region,
            def_region=player.region,
            hq_points=10000,
        )

        war.save()

        schedule, created = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.HOURS)

        war.task = PeriodicTask.objects.create(
            name=f'Война EventWar {war.pk}',
            task='war_round_task',
            interval=schedule,
            args=json.dumps(['EventWar', war.pk, ]),
            start_time=timezone.now()
        )

        war.save()

        war_side_agr = WarSide(
            content_object=war,
            side='agr',
        )
        war_side_agr.save()

        war_side_def = WarSide(
            content_object=war,
            side='def',
        )
        war_side_def.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': 'Ошибка типа запроса',
            'header': 'Основание государства',
            'grey_btn': 'Закрыть',
        }
        return JResponse(data)
