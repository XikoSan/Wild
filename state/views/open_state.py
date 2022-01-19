from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from party.party import Party
from player.decorators.player import check_player
from player.player import Player
from region.region import Region
from state.models.capital import Capital
from state.models.state import State


@login_required(login_url='/')
@check_player
# Opening page with selected state data
def open_state(request, pk):
    # Получаем объект персонажа, по его ключу
    # Текущий пользователь
    player = Player.objects.get(account=request.user)

    state = get_object_or_404(State, pk=pk)
    capital = Capital.objects.get(state=state)

    regions_state = Region.objects.filter(state=state)

    players_count = Player.objects.filter(region__in=regions_state).count()
    parties_count = Party.objects.filter(region__in=regions_state, deleted=False).count()

    characters_pk = Player.objects.only('pk', 'region').filter(region__in=regions_state)

    regions_pop = {}
    for plr in characters_pk:
        if plr.region in regions_pop:
            regions_pop[plr.region] += 1
        else:
            regions_pop[plr.region] = 1

    parties = Party.objects.filter(region__in=regions_state, deleted=False)

    party_characters_pk = Player.objects.only('pk', 'party').filter(party__in=parties)
    
    party_sizes = {}
    for char in party_characters_pk:
        if char.region in party_sizes:
            party_sizes[char.party] += 1
        else:
            party_sizes[char.party] = 1

    return render(request, 'state/state_view.html', {
        'page_name': state.title,
        'player': player,
        'state': state,
        'capital': capital.region,

        'players_count': players_count,
        'parties_count': parties_count,

        'regions_state': regions_state,
        'regions_pop': regions_pop,

        'parties_of_state': parties,
        'party_sizes': party_sizes,

        # 'wars_cnt': wars_cnt,
    })
