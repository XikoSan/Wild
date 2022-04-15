from datetime import datetime

import pytz
import redis
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from player.decorators.player import check_player
from player.player import Player
from wild_politics.settings import TIME_ZONE


@login_required(login_url='/')
@check_player
# Открытие страницы просмотра профиля персонажа
def view_profile(request, pk):
    # Получаем объект персонажа, по его ключу
    # Текущий пользователь
    player = Player.get_instance(account=request.user)
    # Пользователб, чью страницу необходимо просмотреть
    char = get_object_or_404(Player, pk=pk)
    # если игрок хочет посмотреть самого себя
    if player == char:
        # перекидываем его в профиль
        return redirect("my_profile")

    # получим время онлайна игрока
    dtime = None
    r = redis.StrictRedis(host='redis', port=6379, db=0)

    timestamp = r.hget('online', str(char.pk))
    if timestamp:
        dtime = datetime.fromtimestamp(int(timestamp)).replace(tzinfo=pytz.timezone(TIME_ZONE)).astimezone(
            tz=pytz.timezone(player.time_zone)).strftime("%d.%m.%Y %H:%M:%S")

    user_link = ''

    if SocialAccount.objects.filter(user=char.account).exists():
        if SocialAccount.objects.filter(user=char.account).all()[0].provider == 'vk':
            user_link = 'https://vk.com/id' + SocialAccount.objects.filter(user=char.account).all()[0].uid

    # char_settings = None
    # if PlayerSettings.objects.filter(player=char).exists():
    #     char_settings = PlayerSettings.objects.get(player=char)
    # ---------------------
    # cursor = connection.cursor()
    # cursor.execute(
    #     "SELECT COUNT(DISTINCT store.cash + player.cash) FROM gamecore_player AS player JOIN gamecore_storage AS store ON store.owner_id = player.id WHERE store.cash + player.cash >= (SELECT store.cash + player.cash FROM gamecore_player AS player JOIN gamecore_storage AS store ON store.owner_id = player.id WHERE player.id=%s LIMIT 1);",
    #     [char.pk])
    # cash_rating = cursor.fetchone()
    # ---------------------
    return render(request, 'player/view_profile.html', {'player': player,
                                                        'char': char,
                                                        'dtime': dtime,
                                                        'user_link': user_link,

                                                        'page_name': char.nickname,
                                                        })
