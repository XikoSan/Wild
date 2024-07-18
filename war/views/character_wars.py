import pytz
import redis
from allauth.socialaccount.models import SocialAccount
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from player.decorators.player import check_player
from player.player import Player
from player.player_settings import PlayerSettings
from player.views.get_subclasses import get_subclasses
from war.models.wars.war import War
from wild_politics.settings import TIME_ZONE
from player.views.lists.get_thing_page import get_thing_page


@login_required(login_url='/')
@check_player
# Открытие страницы просмотра профиля персонажа
def character_wars(request, pk):
    # Получаем объект персонажа, по его ключу
    # Текущий пользователь
    player = Player.get_instance(account=request.user)
    # Пользователб, чью страницу необходимо просмотреть
    char = get_object_or_404(Player, pk=pk)

    page = request.GET.get('page')

    # соберем строку запроса
    raw_sql = 'SELECT pd.*, COALESCE('

    war_types = get_subclasses(War)

    # добавляем в COALESCE время от всех классов из БД
    for index, war_cl in enumerate(war_types):

        if index == len(war_types) - 1:
            class_time = f'public.war_{war_cl.__name__.lower()}.start_time) AS start_time FROM public.war_playerdamage as pd'
        else:
            class_time = f'public.war_{war_cl.__name__.lower()}.start_time, '

        raw_sql += class_time

    # добавляем подзапросы из всех БД
    for index, war_cl in enumerate(war_types):
        class_subq = f""" 
            LEFT JOIN public.war_{war_cl.__name__.lower()} ON pd.object_id = public.war_{war_cl.__name__.lower()}.id AND pd.content_type_id = (
                SELECT id FROM django_content_type WHERE model = '{war_cl.__name__.lower()}' LIMIT 1
            )
        """
        raw_sql += class_subq

    raw_sql += f'where pd.player_id = {char.id} ORDER BY start_time DESC;'

    #  в итоге выйдет что-то такое (оставил для понимания)

    # raw_sql = """
    #     SELECT pd.*, COALESCE(e.start_time, gw.start_time, re.start_time) AS start_time
    #         FROM public.war_playerdamage as pd
    #
    #     LEFT JOIN public.war_eventwar as e ON pd.object_id = e.id AND pd.content_type_id = (
    #             SELECT id FROM django_content_type WHERE model = 'eventwar' LIMIT 1
    #         )
    #
    #     LEFT JOIN public.war_groundwar as gw ON pd.object_id = gw.id AND pd.content_type_id = (
    #             SELECT id FROM django_content_type WHERE model = 'groundwar' LIMIT 1
    #         )
    #
    #     LEFT JOIN public.war_revolution as re ON pd.object_id = re.id AND pd.content_type_id = (
    #             SELECT id FROM django_content_type WHERE model = 'revolution' LIMIT 1
    #         )
    #
    #     where pd.player_id = 1
    #
    #     ORDER BY start_time DESC;
    # """

    # Выполнение raw SQL запроса
    with connection.cursor() as cursor:
        cursor.execute(raw_sql)
        results = cursor.fetchall()

    # Преобразование результата в список объектов
    player_damage_list = []
    columns = [col[0] for col in cursor.description]
    for row in results:
        player_damage_list.append(dict(zip(columns, row)))



    content_type_ids = []

    for result in player_damage_list:
        content_type_ids.append(result['content_type_id'])

    content_types = ContentType.objects.filter(id__in=content_type_ids)

    ret_list = []

    for result in player_damage_list:
        ret_elem = result.copy()

        content_type = content_types.get(id=result['content_type_id'])
        war_cl = content_type.model_class()
        obj = war_cl.objects.get(id=result['object_id'])

        ret_elem['war'] = obj

        ret_elem['dmg_perc'] = int(ret_elem['damage'] / ( obj.war_side.get(side='agr').count + obj.war_side.get(side='def').count ) * 100)

        ret_elem.pop('content_type_id')
        ret_elem.pop('object_id')

        ret_list.append(ret_elem)


    page = 'war/redesign/character_wars.html'

    return render(request, page, {'page_name': f'Бои: {char.nickname}',
                                  'player': player,
                                  'char': char,

                                  'wars_list': ret_list,
                                  })
