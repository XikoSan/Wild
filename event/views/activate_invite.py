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

from event.models.inviting_event.invite import Invite
from player.decorators.player import check_player
from player.player import Player
from wild_politics.settings import JResponse
from player.logs.prem_log import PremLog


# Открыть лутбоксы
@login_required(login_url='/')
@check_player
@transaction.atomic
def activate_invite(request):
    if request.method == "POST":

        # получаем персонажа игрока
        player = Player.get_instance(account=request.user)

        from player.logs.print_log import log
        log(request.user.date_joined)

        if request.user.date_joined + timedelta(days=3) < timezone.now():
            data = {
                'response': '3 дня с момента регистрации прошли...',
                'header': 'Активация приглашения',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        try:
            sender_pk = int(request.POST.get('code'))

        except ValueError:
            data = {
                'response': 'ID пригласившего указан некорректно',
                'header': 'Активация приглашения',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        invite = Invite(
            sender=Player.get_instance(pk=sender_pk),
            invited=player
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
            'response': _('Ошибка метода'),
            'header': 'Активация приглашения',
            'grey_btn': 'Закрыть',
        }
        return JResponse(data)
