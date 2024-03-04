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
    cursor.execute("with dislikes as( select article_id, COUNT(*) from public.article_article_votes_con group by article_id ), likes as ( select article_id, COUNT(*) from public.article_article_votes_pro group by article_id ) SELECT COALESCE(l.article_id, d.article_id) as article, COALESCE(l.count, 0) - COALESCE(d.count, 0) AS difference FROM likes as l full outer join dislikes as d on d.article_id = l.article_id WHERE COALESCE(l.count, 0) - COALESCE(d.count, 0) > 0 order by difference desc, article desc limit 10;")
    list_db = cursor.fetchall()

    list_articles_pk = []

    for elem in list_db:
        list_articles_pk.append(elem[0])

    article_noorder = Article.objects.defer('body').filter(pk__in=list_articles_pk)

    top_articles = []

    for elem in list_db:
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


    # отправляем в форму
    return render(request, 'article/articles.html', {
        'page_name': 'Статьи',
        # самого игрока
        'player': player,

        # список всех статей
        'articles': article_list,
        # лучшие статьи
        'top_articles': top_articles,
        # список подписок
        'subs_articles': subs_articles,
        # словарь рейтинга статей
        'rating_dict': rating_dict,
    })
