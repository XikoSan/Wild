from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from itertools import chain

from player.decorators.player import check_player
from player.player import Player
from article.models.article import Article


# открыть статью
@login_required(login_url='/')
@check_player
def view_article(request, pk):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    if Article.objects.filter(pk=pk).exists():
        article = Article.objects.get(pk=pk)
    else:
        # перекидываем в список статей
        return redirect("articles")

    # отправляем в форму
    return render(request, 'article/article.html', {
        # самого игрока
        'player': player,
        # статья
        'article': article,
    })
