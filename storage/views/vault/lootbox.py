from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.logs.gold_log import GoldLog
from player.lootbox.lootbox import Lootbox
from player.player import Player


# главная страница
@login_required(login_url='/')
@check_player
def lootbox(request):
    player = Player.get_instance(account=request.user)

    lootbox_count = 0
    if Lootbox.objects.filter(player=player).exists():
        lootbox_count = Lootbox.objects.get(player=player).stock

    today = timezone.now().date()
    was_top_buy = False
    was_buy_today = False

    # проверем покупали ли большие ящики
    if GoldLog.objects.filter(player=player, activity_txt='boxes', gold=40000).exists() \
            or GoldLog.objects.filter(player=player, activity_txt='boxes', gold=75000).exists():
        was_top_buy = True

    # если уже покупали лутбоксы, смотрим, покупали ли сегодня
    if GoldLog.objects.filter(player=player, activity_txt='boxes', dtime__date=today).exists():
        was_buy_today = True

    page = 'storage/redesign/storage_blocks/lootbox.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name': pgettext('assets', 'Сундуки'),

        'player': player,

        'was_top_buy': was_top_buy,
        'was_buy_today': was_buy_today,

        'lootbox_count': lootbox_count,
    })
    return response
