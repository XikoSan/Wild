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
def create_article(request):
    if request.method == "POST":
        player = Player.objects.get(account=request.user)

        if not request.POST.get('title', ''):
            data = {
                'header': 'Новый статья',
                'grey_btn': 'Закрыть',
                'response': 'ID стикерпака должен быть целым числом',
            }
            return JResponse(data)

        body = request.POST.get('text', '').replace('script', 'sсript').replace('style', 'stуlе')

        article = Article(
                        player=player,
                        title=request.POST.get('title', ''),
                        body=body,
                      )

        # settings_code = PlayerSettings.objects.get(player=player).language
        #
        # if settings_code:
        #     art.language = settings_code
        #
        # elif check_for_language(request.LANGUAGE_CODE):
        #     art.language = request.LANGUAGE_CODE

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
            'header': 'Новая статья',
            'grey_btn': 'Закрыть',
        }
        return JResponse(data)