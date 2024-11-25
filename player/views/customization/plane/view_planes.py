from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from region.models.plane import Plane
from storage.models.lootbox_prize import LootboxPrize
from django.utils.translation import pgettext


@login_required(login_url='/')
@check_player
# открытие страницы самолётов
def view_planes(request, pk):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    # Пользователб, чью страницу необходимо просмотреть
    char = get_object_or_404(Player, pk=pk)

    # если игрок хочет посмотреть самого себя
    if player == char:
        # перекидываем его в профиль
        return redirect("plane_select")

    planes = None

    if Plane.objects.filter(player=char).exists():
        planes = Plane.objects.filter(player=char).order_by('plane')

    return render(request, 'player/redesign/customization/view_planes.html', {
        'page_name': pgettext('view_planes', 'Авиация'),
        'player': player,
        'char': char,
        'planes': planes,
    })
