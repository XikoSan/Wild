from django import template

from storage.models.cash_lock import CashLock
from django.db.models import Sum
import time
from player.views.timers import until_recharge

# from gamecore.all_views.header.until_recharge import UntilRecharge
register = template.Library()


@register.inclusion_tag('player/redesign/player_status.html')
def player_status(player):
    locked = CashLock.objects.filter(lock_player=player, deleted=False).aggregate(total_cash=Sum('lock_cash'))

    seconds = until_recharge(player)
    time_text = None

    if seconds > 0:
        time_text = time.strftime('%M:%S', time.gmtime(seconds))

    return {
        'player': player,
        'locked': locked['total_cash'],
        'countdown': seconds,
        'time_text': time_text
    }
