from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.logs.print_log import log
from player.player import Player
from player.views.lists.get_thing_page import get_thing_page
from region.region import Region
import redis
from django.utils import timezone
# список всех регионов игры
# page - открываемая страница
@login_required(login_url='/')
@check_player
def world_regions_list(request):
    # получаем персонажа
    player = Player.objects.get(account=request.user)

    # получаем регионы для текущей страницы
    page = request.GET.get('page')
    regions = Region.objects.all().order_by('pk')

    lines = get_thing_page(regions, page, 50)

    pk_list = []
    for line in lines:
        pk_list.append(line.pk)

    characters_pk = Player.objects.only('pk', 'region').filter(region__pk__in=pk_list)

    regions_pop = {}
    for plr in characters_pk:
        if plr.region in regions_pop:
            regions_pop[plr.region] += 1
        else:
            regions_pop[plr.region] = 1

    regions_online = {}
    r = redis.StrictRedis(host='redis', port=6379, db=0)
    # момент завершения выборов - сейчас. Выбираем, чтобы timestamp был одинаков для всех
    timestamp_now = timezone.now().timestamp()

    for char in characters_pk:
        timestamp = None
        timestamp = r.hget('online', str(char.pk))
        if timestamp:
            # если заходил последние сутки
            if int(timestamp) > timestamp_now - 86400:
                if char.region in regions_online:
                    regions_online[char.region] += 1
                else:
                    regions_online[char.region] = 1


    # отправляем в форму
    return render(request, 'lists/world_regions_list.html', {
        'page_name': _('Регионы игры'),

        'player': player,
        'lines': lines,
        'regions_pop': regions_pop,
        'regions_online': regions_online,

        'regions_count': Region.objects.all().count()
    })
