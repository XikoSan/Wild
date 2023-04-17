import time

from django import template
from django.db.models import Sum

from player.views.timers import until_increase
from player.views.timers import until_recharge
from region.building.hospital import Hospital
from storage.models.cash_lock import CashLock

register = template.Library()


@register.inclusion_tag('player/redesign/player_status.html')
def player_status(player):
    locked = CashLock.objects.filter(lock_player=player, deleted=False).aggregate(total_cash=Sum('lock_cash'))

    seconds = until_recharge(player)
    time_text = None

    if seconds > 0:
        time_text = time.strftime('%M:%S', time.gmtime(seconds))

    increase_time = until_increase(player)
    increase_text = increase_value = None

    if increase_time > 0:
        increase_text = time.strftime('%M:%S', time.gmtime(increase_time))

    # величина ближайшнего прироста
    if player.last_top == 0:
        increase_value = Hospital.indexes[Hospital.get_stat(player.region)[0]['top']]
    else:
        increase_value = Hospital.indexes[player.last_top]

    # узнаем, имеет ли игрок доступ к переводам
    translator = False
    groups = list(player.account.groups.all().values_list('name', flat=True))

    if player.account.is_superuser or 'translator' in groups:
        translator = True

    return {
        'player': player,
        'locked': locked['total_cash'],

        'countdown': seconds,
        'time_text': time_text,

        'increase_time': increase_time,
        'increase_text': increase_text,
        'increase_value': increase_value,

        'translator': translator,
    }
