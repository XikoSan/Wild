from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from player.views.lists.get_thing_page import get_thing_page
from django.utils.translation import ugettext as _
from region.region import Region
from player.player import Player
from player.decorators.player import check_player
from party.party import Party


# список всех партий игры
# page - открываемая страница
@login_required(login_url='/')
@check_player
def region_players_list(request, region_pk):
    # получаем персонажа
    player = Player.objects.get(account=request.user)
    request_region = None

    if Region.objects.filter(pk=region_pk).exists():
        request_region = Region.objects.get(pk=region_pk)
    else:
        return redirect('party')

    # получаем партии для текущей страницы
    page = request.GET.get('page')
    players = Player.objects.filter(banned=False, region=request_region).order_by('nickname')
    lines = get_thing_page(players, page, 50)

    # отправляем в форму
    return render(request, 'lists/region_players_list.html', {
        'page_name': _('Население региона'),

        'player': player,
        'lines': lines,

        'request_region': request_region,

        'players_count': Player.objects.filter(banned=False, region=request_region).count()})
