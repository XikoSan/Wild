from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from player.views.lists.get_thing_page import get_thing_page
from django.utils.translation import ugettext as _
from region.models.region import Region
from player.player import Player
from player.decorators.player import check_player
from party.party import Party
from state.models.state import State


# список всех партий госа
# page - открываемая страница
@login_required(login_url='/')
@check_player
def state_parties_list(request, state_pk):
    # получаем персонажа
    player = Player.get_instance(account=request.user)
    request_state = None

    if State.actual.filter(pk=state_pk).exists():
        request_state = State.actual.get(pk=state_pk)
    else:
        return redirect('overview')

    regions_state = Region.objects.filter(state=request_state)

    # получаем партии для текущей страницы
    page = request.GET.get('page')
    parties = Party.objects.filter(deleted=False, region__in=regions_state).order_by('foundation_date', 'title')
    lines = get_thing_page(parties, page, 50)

    party_sizes = {}
    for party in lines:
        party_sizes[party] = Player.objects.filter(party=party).count()

    # отправляем в форму
    return render(request, 'lists/state_parties_list.html', {
        'page_name': _('Партии региона'),

        'player': player,
        'lines': lines,
        'sizes': party_sizes,

        'request_state': request_state,

        'parties_count': parties.count()
    })
