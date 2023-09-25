from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from region.building.power_plant import PowerPlant
from party.party import Party
from player.decorators.player import check_player
from player.player import Player
from region.models.region import Region
from state.models.capital import Capital
from state.models.state import State
from gov.models.president import President
from gov.models.presidential_voting import PresidentialVoting
from gov.models.minister import Minister


@login_required(login_url='/')
@check_player
# Opening page with selected state data
def open_state(request, pk):
    # Получаем объект персонажа, по его ключу
    # Текущий пользователь
    player = Player.get_instance(account=request.user)
    state = None

    if State.actual.filter(pk=pk).exists():
        state = State.actual.get(pk=pk)

    else:
        return redirect('overview')

    capital = Capital.objects.get(state=state)

    president = None
    last_voting = None
    ministers = None

    if President.objects.filter(state=state).exists():
        president = President.objects.get(state=state)

        if PresidentialVoting.objects.filter(president=president, running=False).exists():
            last_voting = PresidentialVoting.objects.filter(president=president, running=False).order_by('-voting_end').first()

        if Minister.objects.filter(state=state).exists():
            ministers = Minister.objects.filter(state=state)

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
        if char.party in party_sizes:
            party_sizes[char.party] += 1
        else:
            party_sizes[char.party] = 1

    return render(request, 'state/state_view.html', {
        'page_name': state.title,
        'player': player,
        'state': state,
        'capital': capital.region,

        'president': president,
        'last_voting': last_voting,

        'ministers': ministers,

        'players_count': players_count,
        'parties_count': parties_count,

        'regions_state': regions_state,
        'regions_pop': regions_pop,

        'parties_of_state': parties,
        'party_sizes': party_sizes,

        'energy_production': PowerPlant.get_power_production(state=state),
        'energy_consumption': PowerPlant.get_power_consumption(state=state),

        # 'wars_cnt': wars_cnt,
    })
