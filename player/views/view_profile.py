import pytz
import redis
from allauth.socialaccount.models import SocialAccount
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from article.models.article import Article
from ava_border.models.ava_border_ownership import AvaBorderOwnership
from gov.models.minister import Minister
from player.decorators.player import check_player
from player.player import Player
from player.player_settings import PlayerSettings
from region.models.plane import Plane
from war.models.wars.player_damage import PlayerDamage
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

    player_articles = Article.objects.only('pk').filter(player=char).values('pk')

    if player_articles:
        articles_tuple = ()

        for article in player_articles:
            articles_tuple += (article['pk'],)

        cursor.execute(
            "with lines_con as(select count(*) from public.article_article_votes_con where article_id in %s), lines_pro as (select count(*) from public.article_article_votes_pro where article_id in %s) SELECT lines_pro.count - lines_con.count AS difference FROM lines_con, lines_pro;",
            [articles_tuple, articles_tuple])

        carma = cursor.fetchall()[0][0]

    else:
        carma = 0
    # ---------------------

    dmg_sum = PlayerDamage.objects.filter(player=char).aggregate(dmg_sum=Sum('damage'))['dmg_sum']

    if not dmg_sum:
        dmg_sum = 0

    # ---------------------

    if Plane.objects.filter(in_use=True, player=char).exists():
        plane = Plane.objects.get(in_use=True, player=char)
        plane_url = f'/static/img/planes/{plane.plane}/{plane.plane}_{plane.color}.svg'
    else:
        plane_url = '/static/img/planes/nagger/nagger_base.svg'

    # ---------------------

    ava_border = None
    png_use = False
    if AvaBorderOwnership.objects.filter(in_use=True, owner=char).exists():
        border = AvaBorderOwnership.objects.get(in_use=True, owner=char)

        ava_border = border.border
        png_use = border.png_use

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
                                  'carma': carma,

                                  'dmg_sum': dmg_sum,

                                  'party_back': party_back,

                                  'page_name': char.nickname,
                                  'ava_border': ava_border,
                                  'png_use': png_use,
                                  'plane_url': plane_url,
                                  })
