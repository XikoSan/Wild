from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from player.views.lists.get_thing_page import get_thing_page
from django.utils.translation import ugettext as _

from player.player import Player
from player.decorators.player import check_player
from party.party import Party


# список всех партий игры
# page - открываемая страница
@login_required(login_url='/')
@check_player
def world_players_list(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    # получаем партии для текущей страницы
    page = request.GET.get('page')
    players = Player.objects.filter(banned=False).order_by('nickname')
    lines = get_thing_page(players, page, 50)

    # отправляем в форму
    return render(request, 'lists/world_players_list.html', {
        'page_name': _('Мировое население'),

        'player': player,
        'lines': lines,

        'parties_count': Party.objects.filter(deleted=False).count()})
