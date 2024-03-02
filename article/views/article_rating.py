from django.contrib.auth.decorators import login_required
from django.db import transaction

from player.decorators.player import check_player
from player.player import Player
from player.views.get_subclasses import get_subclasses
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.tasks import run_bill
from wild_politics.settings import JResponse
from article.models.article import Article


# новый законопроект
@login_required(login_url='/')
@check_player
@transaction.atomic
def article_rating(request):
    if request.method == "POST":

        if Article.objects.filter(pk=int(request.POST.get('pk'))).exists():

            article = Article.objects.get(pk=int(request.POST.get('pk')))

            rating = article.votes_pro.count() - article.votes_con.count()

            data = {
                'response': 'ok',
                'rating': rating,
            }
            return JResponse(data)

        else:
            data = {
                'response': 'Нет такой статьи',
                'header': 'Рейтинг статьи',
                'grey_btn': 'Закрыть',
            }
            return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': 'Ошибка типа запроса',
            'header': 'Рейтинг статьи',
            'grey_btn': 'Закрыть',
        }
        return JResponse(data)
