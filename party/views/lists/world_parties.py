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
def world_parties_list(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    # получаем партии для текущей страницы
    page = request.GET.get('page')
    parties = Party.objects.filter(deleted=False).order_by('foundation_date', 'title')
    lines = get_thing_page(parties, page, 50)

    party_sizes = {}
    for party in lines:
        party_sizes[party] = Player.objects.filter(party=party).count()

    # отправляем в форму
    return render(request, 'lists/world_parties_list.html', {
        'page_name': _('Партии мира'),

        'player': player,
        'lines': lines,
        'sizes': party_sizes,

        'parties_count': Party.objects.filter(deleted=False).count()})
