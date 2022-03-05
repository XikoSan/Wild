from django import template

from storage.models.cash_lock import CashLock
from django.db.models import Sum
import time
from player.views.timers import until_recharge
from player.views.timers import until_increase

# from gamecore.all_views.header.until_recharge import UntilRecharge
register = template.Library()


@register.inclusion_tag('player/player_status.html')
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

    # пополняем
    if player.last_top == 5:
        increase_value = 16
    elif player.last_top == 4:
        increase_value = 13
    elif player.last_top == 3:
        increase_value = 12
    elif player.last_top == 2:
        increase_value = 11
    else:
        increase_value = 9

    return {
        'player': player,
        'locked': locked['total_cash'],

        'countdown': seconds,
        'time_text': time_text,

        'increase_time': increase_time,
        'increase_text': increase_text,
        'increase_value': increase_value,
    }
