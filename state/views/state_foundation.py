import random

from django.contrib.auth.decorators import login_required
from django.db import transaction

from player.decorators.player import check_player
from player.player import Player
from region.region import Region
from state.models.capital import Capital
from state.models.state import State
from state.models.treasury import Treasury
from wild_politics.settings import JResponse
from state.models.parliament.parliament import Parliament

# основание государства
@login_required(login_url='/')
@check_player
@transaction.atomic
def state_foundation(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.objects.get(account=request.user)

        # если у игрока нет прописки
        if player.region != player.residency:
            player.residency = player.region

        player.save()

        # получаем регион игрока
        region = Region.objects.select_for_update().get(pk=player.region.pk)

        # если в регионе уже есть государство
        if region.state:
            data = {
                'response': 'Государство в этом регионе уже есть',
                'header': 'Основание государства',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

        # создаем новое государство
        state = State(
            title='Республика ' + region.region_name,
            color="%06x" % random.randint(0, 0xFFFFFF),
        )
        state.save()

        region.state = state

        capital = Capital(
            state=state,
            region=region
        )
        capital.save()
        treasury = Treasury(
            state=state,
            region=region
        )
        treasury.save()

        parliament = Parliament(
            state=state
        )
        parliament.save()

        region.save()

        data = {
            'response': 'ok',
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': 'Ошибка типа запроса',
            'header': 'Основание государства',
            'grey_btn': 'Закрыть',
        }
        return JResponse(data)
