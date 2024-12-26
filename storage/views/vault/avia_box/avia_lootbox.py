import math
import os
import pytz
import random
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.translation import pgettext
import json
import redis
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
    lootbox_opened = 0

    if Lootbox.objects.filter(player=player).exists():
        box = Lootbox.objects.get(player=player)
        lootbox_count = box.stock
        lootbox_opened = box.opened

    if not Jackpot.objects.filter(amount__gt=200000).exists():
        jp = Jackpot(amount=10000000)
        jp.save()

    budget = math.ceil(Jackpot.objects.all().first().amount / 2)

    # ----------------------------------------

    redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

    key = f'boxes_{player.pk}'

    # Получение текущих данных игрока
    data = redis_client.get(key)
    if data:
        player_data = json.loads(data)
    else:
        player_data = {"expense": 0, "income": 0}

    # ----------------------------------------

    current_data = redis_client.lrange(f'drops_{player.pk}', 0, -1)
    drop_data = [eval(item) for item in current_data]

    # Перезаписать список в обратном порядке
    drop_data = drop_data[::-1]
    # ----------------------------------------

    page = 'storage/redesign/storage_blocks/avia_box.html'

    http_use = False
    if os.getenv('HTTP_USE'):
        http_use = True

    # отправляем в форму
    response = render(request, page, {
        'page_name': pgettext('assets', 'Ледяные сундуки'),

        'player': player,
        'http_use': http_use,

        'lootbox_count': lootbox_count,
        'lootbox_opened': lootbox_opened,
        'budget': budget,

        'player_data': player_data,
        'drop_data': drop_data,
    })
    return response
