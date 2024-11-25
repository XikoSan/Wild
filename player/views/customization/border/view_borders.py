from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import pgettext
from django.utils.translation import ugettext as _

from ava_border.models.ava_border_ownership import AvaBorderOwnership
from player.decorators.player import check_player
from player.player import Player
from storage.models.lootbox_prize import LootboxPrize


@login_required(login_url='/')
@check_player
# открытие страницы самолётов
def view_borders(request, pk):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    # Пользователб, чью страницу необходимо просмотреть
    char = get_object_or_404(Player, pk=pk)

    # если игрок хочет посмотреть самого себя
    if player == char:
        # перекидываем его в профиль
        return redirect("plane_select")

    borders = None

    if AvaBorderOwnership.objects.filter(owner=char).exists():
        borders = AvaBorderOwnership.objects.filter(owner=char)

    return render(request, 'player/redesign/customization/view_borders.html', {
        'page_name': pgettext('view_borders', 'Просмотр рамок'),
        'player': player,
        'char': char,
        'borders': borders,
    })
