import math
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.lootbox.lootbox import Lootbox
from player.player import Player


# главная страница
@login_required(login_url='/')
@check_player
def lootbox(request):
    if not request.user.is_superuser:
        return redirect('overview')

    player = Player.get_instance(account=request.user)

    lootbox_count = 0
    if Lootbox.objects.filter(player=player).exists():
        lootbox_count = Lootbox.objects.get(player=player).stock

    page = 'storage/redesign/storage_blocks/lootbox.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name': pgettext('assets', 'Сундуки'),

        'player': player,
        'lootbox_count': lootbox_count,
    })
    return response
