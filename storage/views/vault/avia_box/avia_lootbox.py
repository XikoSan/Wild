import math
import pytz
import random
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.logs.gold_log import GoldLog
from player.lootbox.jackpot import Jackpot
from player.lootbox.lootbox import Lootbox
from player.player import Player
from storage.views.vault.avia_box.generate_rewards import prepare_plane_lists


# главная страница
@login_required(login_url='/')
@check_player
def avia_lootbox(request):
    player = Player.get_instance(account=request.user)

    lootbox_count = 0
    lootbox_garant = 100

    if Lootbox.objects.filter(player=player).exists():
        box = Lootbox.objects.get(player=player)
        lootbox_count = box.stock
        lootbox_garant = box.garant_in

    if not Jackpot.objects.filter(amount__gt=200000).exists():
        jp = Jackpot(amount=10000000)
        jp.save()

    budget = math.ceil(Jackpot.objects.all().first().amount / 2)

    page = 'storage/redesign/storage_blocks/avia_box.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name': pgettext('assets', 'Ледяные сундуки'),

        'player': player,

        'lootbox_count': lootbox_count,
        'budget': budget,
    })
    return response
