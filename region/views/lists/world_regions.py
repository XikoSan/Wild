import json
from datetime import datetime
from datetime import timedelta

import pytz
import redis
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.utils.translation import pgettext
from player.decorators.player import check_player
from player.player import Player
from player.views.lists.get_thing_page import get_thing_page
from region.models.region import Region
from wild_politics.settings import TIME_ZONE
from region.views.lists.get_regions_online import get_region_online


# класс региона, в котором его онлайн и население - это поля
class RegionWithPop(Region):
    pk = 0
    online = 0
    pop = 0

    class Meta:
        abstract = True

# список всех регионов игры
# page - открываемая страница
@login_required(login_url='/')
@check_player
def world_regions_list(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    # получаем регионы для текущей страницы
    page = request.GET.get('page')
    if page:
        regions = Region.objects.only('pk', 'region_name', 'on_map_id').all().order_by('pk')[0+((page-1)*50):50*page]
    else:
        regions = Region.objects.only('pk', 'region_name', 'on_map_id').all().order_by('pk')[:50]

    regions_with_pop = []

    for region in regions:
        pop_region = RegionWithPop(
            region_name = region.region_name,
            on_map_id = region.on_map_id
        )
        pop_region.pk = region.pk,
        # почему-то строкой выше айди складывается в формате (123,)
        pop_region.pk = pop_region.pk[0]

        pop_region.pop, pop_region.online, players_online = get_region_online(region)

        regions_with_pop.append(pop_region)

    lines = get_thing_page(regions_with_pop, page, 50)

    header = {

        'on_map_id': {
            'text': '',
            'select_text': pgettext('lists', 'Герб'),
            'visible': 'true'
        },

        'region_name': {
            'text': pgettext('lists', 'Регион'),
            'select_text': pgettext('lists', 'Регион'),
            'visible': 'true'
        },

        'online': {
            'text': pgettext('map', 'Онлайн'),
            'select_text': pgettext('map', 'Онлайн'),
            'visible': 'true'
        },

        'pop': {
            'text': 'Население',
            'select_text': 'Население',
            'visible': 'true'
        }
    }

    # отправляем в форму
    return render(request, 'player/redesign/lists/universal_list.html', {
        'page_name': pgettext('world_regions', 'Регионы игры'),

        'player': player,

        'header': header,
        'lines': lines,
    })
