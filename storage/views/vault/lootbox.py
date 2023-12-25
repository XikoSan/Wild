import math
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.lootbox.lootbox import Lootbox
from player.player import Player
from player.logs.gold_log import GoldLog

# главная страница
@login_required(login_url='/')
@check_player
def lootbox(request):
    player = Player.get_instance(account=request.user)

    lootbox_count = 0
    if Lootbox.objects.filter(player=player).exists():
        lootbox_count = Lootbox.objects.get(player=player).stock

    was_buy = False
    if GoldLog.objects.filter(player=player, activity_txt='boxes').exists():
        was_buy = True

    page = 'storage/redesign/storage_blocks/lootbox.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name': pgettext('assets', 'Сундуки'),

        'player': player,
        'was_buy': was_buy,
        'lootbox_count': lootbox_count,
    })
    return response
