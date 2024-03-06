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
from region.models.region import Region
from wild_politics.settings import TIME_ZONE


# получить число онлайн игроков в указанном реге
def get_region_online(region):

    r = redis.StrictRedis(host='redis', port=6379, db=0)

    # запрашиваем дату последнего обновления онлайна в регионах
    # если информацию обновляли менее часа назад
    timestamp = r.hget('region_' + str(region.pk) + '_online', 'dtime')
    dtime = None
    if timestamp:
        dtime = datetime.fromtimestamp(int(timestamp)).astimezone(pytz.timezone(TIME_ZONE))

    region_pop = 0
    region_online = 0
    players_online = []

    with_timezone = timezone.now().astimezone(pytz.timezone(TIME_ZONE))

    if dtime and dtime > with_timezone + timedelta(hours=-1):

        pop_json_dict = r.hget('region_' + str(region.pk) + '_online', 'pop_dict')
        if pop_json_dict:
            # получаем задампленный словарь онлойна игроков
            region_pop = json.loads(pop_json_dict)

        online_json_dict = r.hget('region_' + str(region.pk) + '_online', 'online_dict')
        if online_json_dict:
            # получаем задампленный словарь онлойна игроков
            region_online = json.loads(online_json_dict)

        players_json_dict = r.hget('region_' + str(region.pk) + '_online', 'players_list')
        if players_json_dict:
            # получаем задампленный словарь онлойна игроков
            players_online = json.loads(players_json_dict)

    else:
        characters_pk = Player.objects.only('pk', 'region').filter(banned=False, region=region)

        region_pop = characters_pk.count()

        characters_pk = characters_pk.filter(account__last_login__gte=timezone.now()+timedelta(days=-1))

        if characters_pk:
            pk_list = []
            for char in characters_pk:
                pk_list.append(str(char.pk))
                players_online.append(str(char.pk))
            # по списку pk игроков мы получаем их онлайн в том же порядке
            online_list = r.hmget('online', pk_list)

            # момент завершения выборов - сейчас. Выбираем, чтобы timestamp был одинаков для всех
            timestamp_now = timezone.now().timestamp()

            index = 0
            for char in characters_pk:
                timestamp = online_list[index]
                if timestamp:
                    # если заходил последние сутки
                    if int(timestamp) > timestamp_now - 86400:
                        region_online += 1

                index += 1

        # загрузить результаты в кэш
        pop_json = json.dumps(region_pop, indent=2, default=str)
        r.hset('region_' + str(region.pk) + '_online', 'pop_dict', pop_json)

        o_json = json.dumps(region_online, indent=2, default=str)
        r.hset('region_' + str(region.pk) + '_online', 'online_dict', o_json)

        o_json = json.dumps(players_online, indent=2, default=str)
        r.hset('region_' + str(region.pk) + '_online', 'players_list', o_json)

        r.hset('region_' + str(region.pk) + '_online', 'dtime', str(timezone.now().timestamp()).split('.')[0])

    return region_pop, region_online, players_online
