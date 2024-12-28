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
from django.utils.timezone import now, timedelta
import redis
from player.decorators.player import check_player
from player.logs.gold_log import GoldLog
from player.lootbox.jackpot import Jackpot
from player.lootbox.lootbox import Lootbox
from player.logs.cash_log import CashLog
from django.db.models import Sum
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
    # Определяем временной диапазон за последние сутки
    last_24_hours = now() - timedelta(days=1)

    # Суммируем значение поля 'cash' для указанных условий
    total_cash = CashLog.objects.filter(
        player=player,
        activity_txt='buy_box',
        dtime__gte=last_24_hours
    ).aggregate(Sum('cash'))['cash__sum']

    blocked = False

    # Если сумма отсутствует, она равна 0
    if total_cash is None:
        total_cash = 0

    from player.logs.print_log import log
    log(total_cash)

    limit = int((10000000 + total_cash)/100000)

    if limit <= 0:
        blocked = True

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

        'blocked': blocked,

        'player_data': player_data,
        'drop_data': drop_data,

        'limit': limit,
    })
    return response
