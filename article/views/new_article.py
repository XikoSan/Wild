from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from itertools import chain

from player.decorators.player import check_player
from player.player import Player
from article.models.article import Article
from article.forms import NewArticleForm


# открыть статью
@login_required(login_url='/')
@check_player
def new_article(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    form = NewArticleForm()

    # отправляем в форму
    return render(request, 'article/new_article.html', {
        'page_name': 'Новая статья',
        # самого игрока
        'player': player,
        # форму статьи
        'form': form,
    })
