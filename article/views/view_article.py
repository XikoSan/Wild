from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from itertools import chain

from player.decorators.player import check_player
from player.player import Player
from article.models.article import Article
from article.models.subscription import Subscription

# открыть статью
@login_required(login_url='/')
@check_player
def view_article(request, pk):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    voted = None
    subscription = False

    if Article.objects.filter(pk=pk).exists():
        article = Article.objects.get(pk=pk)

        if player in article.votes_pro.all():
            voted = 'pro'
        elif player in article.votes_con.all():
            voted = 'con'

        if Subscription.objects.filter(
                                        author=article.player,
                                        player=player
                                       ).exists():
            subscription = True

    else:
        # перекидываем в список статей
        return redirect("articles")

    # отправляем в форму
    return render(request, 'article/article.html', {
        'page_name': article.title,
        # самого игрока
        'player': player,
        # статья
        'article': article,

        # рейтинг статьи
        'article_rating': article.votes_pro.count() - article.votes_con.count(),
        'article_rated_up': article.votes_pro.count(),
        'article_rated_down': article.votes_con.count(),

        # голосовал ли
        'voted': voted,
        # подписан ли
        'subscription': subscription,
    })
