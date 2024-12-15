from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, FloatField, Case, When
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from math import ceil

from gov.models.minister import Minister
from gov.models.president import President
from gov.models.presidential_voting import PresidentialVoting
from metrics.models.daily_gold_by_state import DailyGoldByState
from party.party import Party
from player.decorators.player import check_player
from player.player import Player
from region.building.power_plant import PowerPlant
from region.models.region import Region
from state.models.capital import Capital
from state.models.state import State


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
            last_voting = PresidentialVoting.objects.filter(president=president, running=False).order_by(
                '-voting_end').first()

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

    # ----------
    percentage = 0
    salary = 0

    if president:
        # Вычисляем начало недели (понедельник)
        monday_start = now() - timedelta(days=now().weekday())
        seven_days_ago = monday_start.replace(hour=0, minute=0, second=0, microsecond=0)

        # 2. Суммируем заработанное всеми государствами за последние 7 дней
        total_gold_last_7_days = DailyGoldByState.objects.filter(
            date__gte=seven_days_ago
        ).aggregate(total_gold=Sum('daily_gold'))['total_gold'] or 0

        # 3. Получаем данные по каждому государству: сколько они заработали и какой это процент
        percentage = DailyGoldByState.objects.filter(
            date__gte=seven_days_ago,
            state__pk=pk
        ).annotate(
            state_total=Sum('daily_gold'),
            percentage=Case(
                When(state_total=0, then=0.0),
                default=F('state_total') / total_gold_last_7_days,
                output_field=FloatField(),
            )
        ).aggregate(total_percentage=Sum('percentage'))['total_percentage']

        if not percentage:
            percentage = 0

        salary = ceil(10000 * percentage * 0.33)
    # ----------

    return render(request, 'state/redesign/state_view.html', {
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

        'salary': salary,

        # 'wars_cnt': wars_cnt,
    })
