import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import number_format
from django.db import transaction
from django.utils import timezone
from django.utils import translation
from django.utils.translation import ugettext as _
from django.utils.translation import pgettext
from event.models.inviting_event.cash_event import CashEvent
from event.models.inviting_event.invite import Invite
from player.decorators.player import check_player
from player.logs.cash_log import CashLog
from player.logs.prem_log import PremLog
from player.player import Player
from wild_politics.settings import JResponse


# Открыть лутбоксы
@login_required(login_url='/')
@check_player
@transaction.atomic
def activate_invite(request):
    if request.method == "POST":

        if not CashEvent.objects.filter(running=True, event_start__lt=timezone.now(),
                                        event_end__gt=timezone.now()).exists():
            data = {
                'response': pgettext('game_event', 'Событие неактивно'),
                'header': pgettext('game_event', 'Активация приглашения'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        event = CashEvent.objects.get(running=True, event_start__lt=timezone.now(),
                                      event_end__gt=timezone.now())
        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        # если уже приглашен - то все
        if Invite.objects.filter(invited=player, event=event).exists():
            data = {
                'response': pgettext('game_event', 'Игрок уже приглашен'),
                'header': pgettext('game_event', 'Активация приглашения'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        if CashEvent.objects.filter(pk=2).exists():
            prev_event = CashEvent.objects.get(pk=2)
            # если приглашался в прошлом сезоне - то все
            if Invite.objects.filter(invited=player, event=prev_event).exists():
                data = {
                    'response': pgettext('game_event', 'Вы участвовали в прошлом сезоне события'),
                    'header': pgettext('game_event', 'Активация приглашения'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JResponse(data)

        returned = False

        if request.user.date_joined + timedelta(days=3) < timezone.now():
            # если фармил последний месяц - значит активный
            if CashLog.objects.filter(
                    player=player,
                    dtime__gt=timezone.now() - timedelta(days=30),
                    activity_txt='daily'
            ).exists():
                data = {
                    'response': pgettext('game_event', '3 дня с момента регистрации прошли...'),
                    'header': pgettext('game_event', 'Активация приглашения'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JResponse(data)

            else:
                returned = True

        try:
            sender_pk = int(request.POST.get('code'))

        except ValueError:
            data = {
                'response': pgettext('game_event', 'ID пригласившего указан некорректно'),
                'header': pgettext('game_event', 'Активация приглашения'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        exp = 0
        if returned:
            exp = player.power + player.knowledge + player.endurance

        invite = Invite(
            sender=Player.get_instance(pk=sender_pk),
            invited=player,
            exp=exp,
            event=event,
        )
        invite.save()

        # время, к которому прибавляем 7 дней
        if player.premium > timezone.now():
            from_time = player.premium
        else:
            from_time = timezone.now()

        player.premium = from_time + relativedelta(days=7)
        player.save()

        prem_log = PremLog(player=player, days=7, activity_txt='bonus')
        prem_log.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('game_event', 'Активация приглашения'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
