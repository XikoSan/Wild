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


# список всех регионов игры
# page - открываемая страница
@login_required(login_url='/')
@check_player
def world_regions_list(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    # получаем регионы для текущей страницы
    page = request.GET.get('page')
    regions = Region.objects.all().order_by('pk')

    lines = get_thing_page(regions, page, 50)

    pk_list = []
    for line in lines:
        pk_list.append(line.pk)

    r = redis.StrictRedis(host='redis', port=6379, db=0)

    # запрашиваем дату последнего обновления онлайна в регионах
    # если информацию обновляли менее часа назад
    timestamp = r.hget('regions_online', 'dtime')
    dtime = None
    if timestamp:
        dtime = datetime.fromtimestamp(int(timestamp)).astimezone(pytz.timezone(TIME_ZONE))

    regions_pop = {}
    regions_online = {}

    with_timezone = timezone.now().astimezone(pytz.timezone(TIME_ZONE))

    if dtime and dtime > with_timezone + timedelta(hours=-1):

        pop_json_dict = r.hget('regions_online', 'pop_dict')
        if pop_json_dict:
            # получаем задампленный словарь онлойна игроков
            regions_pop_tmp = json.loads(pop_json_dict)
            # переводим словарик из текстового ключа в числовой
            for text_key in regions_pop_tmp.keys():
                val = regions_pop_tmp[text_key]
                regions_pop[int(text_key)] = val

        online_json_dict = r.hget('regions_online', 'online_dict')
        if online_json_dict:
            # получаем задампленный словарь онлойна игроков
            regions_online_tmp = json.loads(online_json_dict)
            # переводим словарик из текстового ключа в числовой
            for text_key in regions_online_tmp.keys():
                val = regions_online_tmp[text_key]
                regions_online[int(text_key)] = val

    else:
        characters_pk = Player.objects.only('pk', 'region').filter(region__pk__in=pk_list)

        regions_pop = {}
        for plr in characters_pk:
            if plr.region.pk in regions_pop:
                regions_pop[plr.region.pk] += 1
            else:
                regions_pop[plr.region.pk] = 1

        pk_list = []
        for char in characters_pk:
            pk_list.append(str(char.pk))
        # по списку pk игроков мы получаем их онлайн в том же порядке
        online_list = r.hmget('online', pk_list)

        # момент завершения выборов - сейчас. Выбираем, чтобы timestamp был одинаков для всех
        timestamp_now = timezone.now().timestamp()

        regions_online = {}

        index = 0
        for char in characters_pk:
            timestamp = None
            timestamp = online_list[index]
            if timestamp:
                # если заходил последние сутки
                if int(timestamp) > timestamp_now - 86400:
                    if char.region.pk in regions_online:
                        regions_online[char.region.pk] += 1
                    else:
                        regions_online[char.region.pk] = 1
            index += 1

        # загрузить результаты в кэш
        pop_json = json.dumps(regions_pop, indent=2, default=str)
        r.hset('regions_online', 'pop_dict', pop_json)

        o_json = json.dumps(regions_online, indent=2, default=str)
        r.hset('regions_online', 'online_dict', o_json)

        r.hset('regions_online', 'dtime', str(timezone.now().timestamp()).split('.')[0])

    # отправляем в форму
    return render(request, 'lists/world_regions_list.html', {
        'page_name': _('Регионы игры'),

        'player': player,
        'lines': lines,
        'regions_pop': regions_pop,
        'regions_online': regions_online,

        'regions_count': Region.objects.all().count()
    })
