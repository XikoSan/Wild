from django import template

from storage.models.cash_lock import CashLock
from django.db.models import Sum
import time
from player.views.timers import until_recharge
from player.views.timers import until_increase
from region.building.hospital import Hospital

from player.player_settings import PlayerSettings
register = template.Library()


@register.inclusion_tag('player/redesign/player_colors.html')
def player_colors(player):

    setts = None

    color_back = '28353E'
    color_block = '284E64'
    color_text = 'FFFFFF'
    color_acct = 'EB9929'

    if PlayerSettings.objects.filter(player=player).exists():
        setts = PlayerSettings.objects.get(player=player)

        color_back  = setts.color_back
        color_block = setts.color_block
        color_text  = setts.color_text
        color_acct  = setts.color_acct

    return {
        'color_back': color_back,
        'color_block': color_block,
        'color_text': color_text,
        'color_acct': color_acct,
    }
