from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils.translation import pgettext
from itertools import chain

from article.forms import NewArticleForm
from article.models.article import Article
from player.decorators.player import check_player
from player.player import Player


# открыть статью
@login_required(login_url='/')
@check_player
def new_article(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    if player.articles_ban:
        return redirect('articles')

    form = NewArticleForm()

    # отправляем в форму
    return render(request, 'article/new_article.html', {
        'page_name': pgettext('new_article', 'Новая статья'),
        # самого игрока
        'player': player,
        # форму статьи
        'form': form,
    })
