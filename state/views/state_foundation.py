import random
from django.contrib.auth.decorators import login_required
from django.db import transaction

from bill.models.independence import Independence
from player.decorators.player import check_player
from player.player import Player
from region.models.region import Region
from state.models.capital import Capital
from state.models.parliament.parliament import Parliament
from state.models.state import State
from django.utils import timezone
from state.models.treasury import Treasury
from war.models.wars.revolution.revolution import Revolution
from wild_politics.settings import JResponse
from datetime import timedelta
from django.utils.translation import pgettext

# основание государства
@login_required(login_url='/')
@check_player
@transaction.atomic
def state_foundation(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        # если у игрока нет прописки
        if player.region != player.residency:
            player.residency = player.region

        player.save()

        # получаем регион игрока
        region = Region.objects.select_for_update().get(pk=player.region.pk)

        # если в регионе уже есть государство
        if region.state:
            data = {
                'response': pgettext('state_foundation', 'Государство в этом регионе уже есть'),
                'header': pgettext('state_foundation', 'Основание государства'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        if Revolution.objects.filter(
                                        running=False,
                                        hq_points__lt=0,
                                        deleted=False,
                                        end_time__gt=timezone.now() - timedelta(hours=12),
                                        def_region=region,
                                     ).exists():
            data = {
                'response': pgettext('state_foundation', 'Невозможно создать государство в первые 12 часов после восстания'),
                'header': pgettext('state_foundation', 'Основание государства'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

        if Independence.objects.filter(
                                        running=False,
                                        type='ac',
                                        voting_end__gt=timezone.now() - timedelta(hours=12),
                                        region=region,
                                     ).exists():
            data = {
                'response': pgettext('state_foundation',
                                     'Невозможно создать государство в первые 12 часов после объявления независимости'),
                'header': pgettext('state_foundation', 'Основание государства'),
                'grey_btn': pgettext('core', 'Закрыть'),
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
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('state_foundation', 'Основание государства'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
