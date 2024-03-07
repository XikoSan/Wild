from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from itertools import chain
from django.db import connection
from player.decorators.player import check_player
from player.player import Player
from article.models.article import Article
from article.models.subscription import Subscription
from django.db.models import Count
from django.utils import timezone
import datetime


# страница войн
@login_required(login_url='/')
@check_player
def articles(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    rating_dict = {}

    article_list = Article.objects.defer('body').all().order_by('-id')[:25]

    for article in article_list:
        rating_dict[article.pk] = article.votes_pro.count() - article.votes_con.count()
    # --------------------------------------------------------------------------------
    # получим лучшие статьи

    cursor = connection.cursor()
    cursor.execute("with dislikes as( select article_id, COUNT(*) from public.article_article_votes_con group by article_id ), likes as ( select article_id, COUNT(*) from public.article_article_votes_pro group by article_id ) SELECT COALESCE(l.article_id, d.article_id) as article, COALESCE(l.count, 0) - COALESCE(d.count, 0) AS difference FROM likes as l full outer join dislikes as d on d.article_id = l.article_id WHERE COALESCE(l.count, 0) - COALESCE(d.count, 0) > 0 order by difference desc, article desc;")
    list_db = cursor.fetchall()

    list_articles_pk = []

    for elem in list_db:
        list_articles_pk.append(elem[0])

    article_noorder = Article.objects.defer('body').filter(pk__in=list_articles_pk).exclude(player__pk=1)

    top_articles = []

    for elem in list_db:
        if len(top_articles) < 10:
            if article_noorder.filter(pk=elem[0]).exists():
                top_articles.append(article_noorder.get(pk=elem[0]))

    # top_articles = Article.objects.annotate(vote_diff=Count('votes_pro') - Count('votes_con')
    #                                         ).filter(vote_diff__gt=0).order_by('-vote_diff', '-id')[:25]
    for article in top_articles:
        if article.pk not in rating_dict.keys():
            rating_dict[article.pk] = article.votes_pro.count() - article.votes_con.count()
    # --------------------------------------------------------------------------------
    # получим подписки игрока
    subs_articles = None
    authors = []

    if Subscription.objects.filter(player=player).exists():

        subscriptions = Subscription.objects.filter(player=player)

        for subscription in subscriptions:
            authors.append(subscription.author)

    subs_articles = Article.objects.defer('body').filter(
                                                            Q(player__in=authors)
                                                            | Q(player__pk=1)
                                                        ).order_by('-id')
    for article in subs_articles:
        if article.pk not in rating_dict.keys():
            rating_dict[article.pk] = article.votes_pro.count() - article.votes_con.count()
    # --------------------------------------------------------------------------------

    # узнаем, может ли игрок дальше постить
    # 0 - 100 кармы = 3 поста в день
    # 100+ кармы = + 1 пост в день
    # 10 постов максимум
    can_post = True

    # сколько уже напощено
    posted_count = Article.objects.filter(player=player, date__gt=timezone.now() - datetime.timedelta(days=1)).count()

    # сколько кармы. За каждые 100 кармы можно +1 пост в день
    player_articles = Article.objects.only('pk').filter(player=player).values('pk')

    if player_articles:
        articles_tuple = ()

        for article in player_articles:
            articles_tuple += (article['pk'],)

        cursor.execute("with lines_con as(select count(*) from public.article_article_votes_con where article_id in %s), lines_pro as (select count(*) from public.article_article_votes_pro where article_id in %s) SELECT lines_pro.count - lines_con.count AS difference FROM lines_con, lines_pro;", [articles_tuple, articles_tuple])

        carma = cursor.fetchall()[0][0]

    else:
        carma = 0

    limit = 3

    if carma < 0:
        limit = 1

    elif carma > 100:
        limit += carma // 100

        if limit > 10:
            limit = 10

    if posted_count >= limit:
        can_post = False

    # отправляем в форму
    return render(request, 'article/articles.html', {
        'page_name': 'Статьи',
        # самого игрока
        'player': player,

        # разрешение постить
        'can_post': can_post,

        # список всех статей
        'articles': article_list,
        # лучшие статьи
        'top_articles': top_articles,
        # список подписок
        'subs_articles': subs_articles,
        # словарь рейтинга статей
        'rating_dict': rating_dict,
    })
