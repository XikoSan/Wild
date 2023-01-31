import json
from datetime import datetime
from datetime import timedelta

import pytz
import redis
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from player.views.lists.get_thing_page import get_thing_page
from region.region import Region
from wild_politics.settings import TIME_ZONE
from region.views.lists.get_regions_online import get_region_online

# список всех регионов игры
# page - открываемая страница
@login_required(login_url='/')
@check_player
def world_regions_list(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    # получаем регионы для текущей страницы
    page = request.GET.get('page')
    regions = Region.objects.only('pk', 'region_name', 'on_map_id').all().order_by('pk')

    lines = get_thing_page(regions, page, 50)

    pk_list = []
    for line in lines:
        pk_list.append(line.pk)

    regions_pop = {}
    regions_online = {}

    for region in regions.filter(pk__in=pk_list):
        regions_pop[region.pk], regions_online[region.pk] = get_region_online(region)

    # отправляем в форму
    return render(request, 'lists/world_regions_list.html', {
        'page_name': _('Регионы игры'),

        'player': player,
        'lines': lines,
        'regions_pop': regions_pop,
        'regions_online': regions_online,

        'regions_count': Region.objects.all().count()
    })
