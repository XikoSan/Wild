import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask, CrontabSchedule, ClockedSchedule
from datetime import timedelta

from player.decorators.player import check_player
from player.player import Player
from war.models.wars.event_war import EventWar
from war.models.wars.war_side import WarSide
from wild_politics.settings import JResponse
from django.utils.translation import pgettext


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
        player = Player.get_instance(account=request.user)

        # создаем новую войну
        war = EventWar(
            running=True,
            start_time=timezone.now(),
            agr_region=player.region,
            def_region=player.region,

            hq_points=10000,
        )

        war.save()

        schedule, created = CrontabSchedule.objects.get_or_create(
                                                    minute='*',
                                                    hour='*',
                                                    day_of_week='*',
                                                    day_of_month='*',
                                                    month_of_year='*',
                                                   )

        war.task = PeriodicTask.objects.create(
            enabled = True,
            name=f'Война EventWar {war.pk}',
            task='war_round_task',
            # interval=schedule,
            crontab=schedule,
            args=json.dumps(['EventWar', war.pk, ]),
            start_time=timezone.now()
        )

        end_time = timezone.now() + timedelta(days=1)  # Текущее время + 24 часа

        clocked_schedule, created = ClockedSchedule.objects.get_or_create(
            clocked_time=end_time,
        )

        war.end_task = PeriodicTask.objects.create(
            enabled = True,
            name=f'Завершение войны EventWar {war.pk}',
            task='end_war',
            clocked=clocked_schedule,
            one_off=True,
            args=json.dumps(['EventWar', war.pk]),
            start_time=timezone.now()
        )

        war.end_task.save()

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
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('state_foundation', 'Основание государства'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
