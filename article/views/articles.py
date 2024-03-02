from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from itertools import chain

from player.decorators.player import check_player
from player.player import Player
from article.models.article import Article


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

    # отправляем в форму
    return render(request, 'article/articles.html', {
        'page_name': 'Статьи',
        # самого игрока
        'player': player,
        # список всех статей
        'articles': article_list,
        # словарь рейтинга статей
        'rating_dict': rating_dict,
    })
