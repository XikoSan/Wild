from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from itertools import chain

from player.decorators.player import check_player
from player.player import Player
from article.models.article import Article
from article.forms import NewArticleForm
from wild_politics.settings import JResponse


# открыть статью
@login_required(login_url='/')
@check_player
def change_article(request):
    if request.method == "POST":
        player = Player.objects.get(account=request.user)

        if not request.POST.get('article_pk'):
            data = {
                'header': 'Редактировать статью',
                'grey_btn': 'Закрыть',
                'response': 'ID статьи не передан',
            }
            return JResponse(data)

        try:
            article_pk = int(request.POST.get('article_pk'))

        except ValueError:
            data = {
                'header': 'Редактировать статью',
                'grey_btn': 'Закрыть',
                'response': 'ID статьи должно быть целым числом',
            }
            return JResponse(data)

        if not Article.objects.filter(pk=article_pk).exists():
            data = {
                'header': 'Редактировать статью',
                'grey_btn': 'Закрыть',
                'response': 'Неизвестная статья',
            }
            return JResponse(data)

        article = Article.objects.get(pk=article_pk)

        body = request.POST.get('text', '').replace('script', 'sсript')

        if not body:
            data = {
                'header': 'Редактировать статью',
                'grey_btn': 'Закрыть',
                'response': 'Текст статьи не должен быть пустым',
            }
            return JResponse(data)

        article.body = body

        article.save()

        data = {
            'response': 'ok',
            'id': article.pk
        }
        return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            # 'response': _('positive_enrg_req'),
            'response': 'Ошибка типа запроса',
            'header': 'Редактировать статью',
            'grey_btn': 'Закрыть',
        }
        return JResponse(data)