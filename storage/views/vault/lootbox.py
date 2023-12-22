import math
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player
from region.views.distance_counting import distance_counting
from storage.models.storage import Storage
from storage.models.transport import Transport
from datetime import datetime
from storage.views.storage.locks.get_storage import get_stocks
from storage.models.good import Good
from storage.models.stock import Stock


# главная страница
@login_required(login_url='/')
@check_player
def lootbox(request):
    player = Player.get_instance(account=request.user)

    page = 'storage/redesign/storage_blocks/lootbox.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name': pgettext('assets', 'Сундуки'),

        'player': player,
        # 'storages': storages,
    })
    return response
