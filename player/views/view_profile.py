import pytz
import redis
from allauth.socialaccount.models import SocialAccount
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from gov.models.minister import Minister
from player.decorators.player import check_player
from player.player import Player
from player.player_settings import PlayerSettings
from wild_politics.settings import TIME_ZONE
from ava_border.models.ava_border_ownership import AvaBorderOwnership


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

    minister = None
    if Minister.objects.filter(player=char).exists():
        minister = Minister.objects.get(player=char)

    # char_settings = None
    # if PlayerSettings.objects.filter(player=char).exists():
    #     char_settings = PlayerSettings.objects.get(player=char)
    # ---------------------
    cursor = connection.cursor()
    cursor.execute(
        "with sum_limit (lim) as ( select SUM(store.cash) + player.cash from player_player as player join storage_storage as store on player.id = %s and store.owner_id = player.id and store.deleted = false group by player.id ), store_sum (owner_id, cash) as ( select store.owner_id, sum(store.cash) from storage_storage as store where store.deleted = false group by store.owner_id ) select count ( * ) + 1 from player_player as player join store_sum as store on store.owner_id = player.id where store.cash + player.cash > ( select lim from sum_limit );",
        [char.pk])
    cash_rating = cursor.fetchone()
    # ---------------------

    ava_border = None
    if AvaBorderOwnership.objects.filter(in_use=True, owner=char).exists():
        ava_border = AvaBorderOwnership.objects.get(in_use=True, owner=char).border

    party_back = True

    if PlayerSettings.objects.filter(player=char).exists():
        party_back = PlayerSettings.objects.get(player=char).party_back

    groups = list(player.account.groups.all().values_list('name', flat=True))
    page = 'player/view_profile.html'
    if 'redesign' not in groups:
        page = 'player/redesign/view_profile.html'

    return render(request, page, {'player': player,
                                  'char': char,
                                  'minister': minister,
                                  'dtime': dtime,
                                  'user_link': user_link,
                                  'cash_rating': cash_rating[0],

                                  'party_back': party_back,

                                  'page_name': char.nickname,
                                  'ava_border': ava_border,
                                  })
