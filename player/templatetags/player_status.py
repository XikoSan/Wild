from django import template

from storage.models.cash_lock import CashLock
from django.db.models import Sum

# from gamecore.all_views.header.until_recharge import UntilRecharge
register = template.Library()


@register.inclusion_tag('player/player_status.html')
def player_status(player):

    locked = CashLock.objects.filter(lock_player=player, deleted=False).aggregate(total_cash=Sum('lock_cash'))

    return {
        'player': player,
        'locked': locked['total_cash'],
        # 'countdown': UntilRecharge(player)
    }
