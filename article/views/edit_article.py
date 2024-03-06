from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from itertools import chain

from player.decorators.player import check_player
from player.player import Player
from article.models.article import Article
from article.forms import NewArticleForm
from article.models.article import Article

# открыть статью
@login_required(login_url='/')
@check_player
def edit_article(request, pk):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    if Article.objects.filter(pk=pk).exists():
        article = Article.objects.get(pk=pk)
    else:
        return redirect('articles')

    if article.player != player:
        return redirect("view_article", pk=pk)

    form = NewArticleForm(initial={'text': article.body})

    # отправляем в форму
    return render(request, 'article/edit_article.html', {
        'page_name': f'Редактировать: { article.title }',
        # самого игрока
        'player': player,
        # форму статьи
        'form': form,
        # id статьи
        'article_pk': article.pk,
    })
