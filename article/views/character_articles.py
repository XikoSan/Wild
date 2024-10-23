import pytz
import redis
from allauth.socialaccount.models import SocialAccount
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import pgettext

from article.models.article import Article
from player.decorators.player import check_player
from player.player import Player
from player.player_settings import PlayerSettings
from wild_politics.settings import TIME_ZONE


@login_required(login_url='/')
@check_player
# Открытие страницы просмотра профиля персонажа
def character_articles(request, pk):
    # Получаем объект персонажа, по его ключу
    # Текущий пользователь
    player = Player.get_instance(account=request.user)
    # Пользователб, чью страницу необходимо просмотреть
    char = get_object_or_404(Player, pk=pk)

    rating_dict = {}

    article_list = Article.objects.defer('body').filter(player=char).order_by('-id')

    for article in article_list:
        rating_dict[article.pk] = article.votes_pro.count() - article.votes_con.count()

    page = 'article/character_articles.html'

    return render(request, page,
                  {'page_name': pgettext('article', "Статьи: %(nickname)s") % {"nickname": char.nickname},
                   'player': player,
                   'char': char,

                   # список всех статей
                   'articles': article_list,
                   # словарь рейтинга статей
                   'rating_dict': rating_dict,
                   })
