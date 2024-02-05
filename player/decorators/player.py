# coding=utf-8
import os
import pytz
import redis
from datetime import datetime
from django.apps import apps
from django.db.models import Q
from django.shortcuts import redirect
from django.utils import timezone
from django.utils import translation
from django.utils.translation import check_for_language
from datetime import timedelta

# from event.models.enter_event.activity_event import ActivityEvent
# from event.models.enter_event.event_part import ActivityEventPart
# from event.models.enter_event.global_part import ActivityGlobalPart
# from player.player_settings import PlayerSettings
from wild_politics.settings import TIME_ZONE


# Декоратор для проверки того, что:
#   1. Игрок от даного аккаунта существует
#   2. Этот игрок не забанен

# Декоратор получает на вход функцию
# В передающейся функции первым аргументом должен идти параметр request,
# а дальше произвольное кол-во аргументов
def check_player(func):
    # Создаем обёртывающую функцию для переданной func
    # Функция получает объект запроса - request(ведь, любое представление его получает)
    # и, если надо, переменное кол-во других аргументов, позиционных - *args и именованных - **kwargs
    def checking(request, *args, **kwargs):
        # Проходим все необходимые проверки:
        # Если у игрока есть хоть один персонаж:
        Player = apps.get_model('player.Player')
        PlayerSettings = apps.get_model('player.PlayerSettings')

        if Player.objects.filter(account=request.user).exists():
            # Получаем игрока
            player = Player.objects.only('pk', 'user_ip', 'natural_refill', 'energy', 'region', 'last_top',
                                         'banned').get(account=request.user)
            # язык из настроек
            if PlayerSettings.objects.filter(player=player).exists():
                player_settings = PlayerSettings.objects.get(player=player)
                if player_settings.language:
                    translation.activate(player_settings.language)

            # проверяем, нужно ли начислить бонус за вход
            activity_event_check(player)

            # записываем время последнего онлайна
            r = redis.StrictRedis(host='redis', port=6379, db=0)

            r.hset('online', str(player.pk), str(timezone.now().timestamp()).split('.')[0])

            # Получаем текущий ip игрока
            cur_ip = get_client_ip(request)
            # присваиваем ему этот адрес
            player.user_ip = cur_ip
            player.save()

            # Тут добавить УЗ суперов для обхода блокировки.
            if player.pk == 1 or request.user.is_staff:
                # if True:
                # Возвращение выполнения основной(переданной в check_player)
                # функции - func, с переданными ей аргументами - *args и **kwargs
                return func(request, *args, **kwargs)
            else:

                # проверка на IP работает только на продакшене
                # if os.environ.get('PROD'):
                # если найдены игроки с таким же ip как найденный, не считая самого игрока
                if Player.objects.filter(user_ip=cur_ip).exclude(
                        Q(pk=player.pk) |
                        Q(pk=491) | Q(pk=498) |
                        Q(banned=True)
                ).exists():

                    players = Player.objects.filter(user_ip=cur_ip)
                    for it_player in players:
                        it_player.banned = True
                        it_player.reason = 'один айпи'
                        it_player.save()
                    player.banned = True
                    player.reason = 'один айпи'

                # Если игрок не забанен:
                if not player.banned:
                    # Возвращение выполнения основной(переданной в check_player)
                    # функции - func, с переданными ей аргументами - *args и **kwargs
                    return func(request, *args, **kwargs)
                # Если же забанен:
                else:
                    # Перенаправляем на страницу бана
                    return redirect('banned')
        # Если у игрока нет персонажей:
        else:
            # Пусть идет создавать нового
            return redirect('new_player')

    # Возвращаем проверяющую функцию
    return checking


# Получение IP игрока
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def activity_event_check(player):
    r = redis.StrictRedis(host='redis', port=6379, db=0)

    ActivityEvent = apps.get_model('event.ActivityEvent')

    # узнаем, есть ли активный ивент логинов
    if ActivityEvent.objects.filter(running=True,
                                    event_start__lt=timezone.now(),
                                    event_end__gt=timezone.now()
                                    ).exists():
        # узнаем время предыдущего онлайна
        timestamp = r.hget('online', str(player.pk))
        if timestamp:
            prev_dtime = datetime.fromtimestamp(int(timestamp)).replace(tzinfo=pytz.timezone(TIME_ZONE))

            # если есть информация о предыдущем онлайне, и это разные сутки с текущей датой
            if prev_dtime.date() != datetime.now().date():

                if prev_dtime.date() == datetime.now().date() - timedelta(days=1):
                    activity_event_reward(player, 1)

                elif prev_dtime.date() != datetime.now().date() - timedelta(days=1):
                    activity_event_reward(player, -1)



def activity_event_reward(player, mod):

    ActivityEvent = apps.get_model('event.ActivityEvent')
    ActivityEventPart = apps.get_model('event.ActivityEventPart')
    ActivityGlobalPart = apps.get_model('event.ActivityGlobalPart')

    activity_event = ActivityEvent.objects.get(running=True,
                                               event_start__lt=timezone.now(),
                                               event_end__gt=timezone.now()
                                               )
    event_part = None

    if ActivityEventPart.objects.filter(
            player=player,
            event=activity_event
    ).exists():

        event_part = ActivityEventPart.objects.get(
            player=player,
            event=activity_event
        )

        if event_part.points + mod >= 0:
            event_part.points += mod
            event_part.prize_check()
            event_part.save()

    else:
        if mod == 1:
            event_part = ActivityEventPart(
                player=player,
                event=activity_event,
                points=mod
            )


        else:
            event_part = ActivityEventPart(
                player=player,
                event=activity_event,
                points=0
            )

        event_part.prize_check()
        event_part.save()

    #       ---- общий счет ----
    if ActivityGlobalPart.objects.filter(
            event=activity_event
    ).exists():

        global_part = ActivityGlobalPart.objects.get(
            event=activity_event
        )
        if global_part.points + mod >= 0:
            global_part.points += mod
            event_part = global_part.prize_check(event_part)
            event_part.save()
            global_part.save()

    else:
        if mod == 1:
            global_part = ActivityGlobalPart(
                event=activity_event,
                points=mod
            )

            event_part = global_part.prize_check(event_part)
            event_part.save()
            global_part.save()