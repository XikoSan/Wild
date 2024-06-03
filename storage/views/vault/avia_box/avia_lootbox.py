from datetime import datetime, timedelta
import pytz
import random
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.logs.gold_log import GoldLog
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

    page = 'storage/redesign/storage_blocks/avia_box.html'

    common_list = prepare_plane_lists(player, 'common')
    rare_list = prepare_plane_lists(player, 'rare')
    epic_list = prepare_plane_lists(player, 'epic')

    cleared_common = []
    for elem in common_list:
        if not elem[0] == 'beluzzo':
            cleared_common.append(elem)
    randint = random.randint(1, len(cleared_common) - 2)
    common_slice = cleared_common[randint - 1: randint + 2]

    randint = random.randint(1, len(rare_list) - 2)
    rare_slice = rare_list[randint - 1: randint + 2]

    randint = random.randint(1, len(epic_list) - 2)
    epic_slice = epic_list[randint - 1: randint + 2]

    # -----------------------------------
    sold_packs = []
    date_msk = datetime(2024, 6, 2, 22, 0, 0)
    timezone_msk = pytz.timezone('Europe/Moscow')
    date_msk = timezone_msk.localize(date_msk)

    for box_price in [4500, 8500, 45000, 85000]:
        # проверем покупали ли большие ящики
        if GoldLog.objects.filter(player=player, activity_txt='boxes', gold=0-box_price,
                                  dtime__gt=date_msk).exists():
            sold_packs.append(box_price)

    # -----------------------------------

    # отправляем в форму
    response = render(request, page, {
        'page_name': pgettext('assets', 'Аэрокейсы'),

        'player': player,

        'common_list': common_list,
        'rare_list': rare_list,
        'epic_list': epic_list,

        'common_slice': common_slice,
        'rare_slice': rare_slice,
        'epic_slice': epic_slice,

        'lootbox_count': lootbox_count,
        'garant_count': lootbox_garant,

        'variants': len(common_list) + len(rare_list) + len(epic_list) + 5,
        'sold_packs': sold_packs,
    })
    return response
