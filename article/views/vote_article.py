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
from django.utils.translation import pgettext

# новый законопроект
@login_required(login_url='/')
@check_player
@transaction.atomic
def vote_article(request):
    if request.method == "POST":
        # получаем персонажа
        player = Player.get_instance(account=request.user)

        if Article.objects.filter(pk=int(request.POST.get('pk'))).exists():

            article = Article.objects.select_for_update().get(pk=int(request.POST.get('pk')))

            votes_pro = article.votes_pro.all()
            votes_con = article.votes_con.all()

            if request.POST.get('mode') == 'pro':

                if player in votes_con:
                    article.votes_con.remove(player)

                article.votes_pro.add(player)

            elif request.POST.get('mode') == 'con':

                if player in votes_pro:
                    article.votes_pro.remove(player)

                article.votes_con.add(player)

            else:
                data = {
                    'response': pgettext('vote_article', 'Не выбрана оценка статьи'),
                    'header': pgettext('vote_article', 'Оценить статью'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }
                return JResponse(data)

            rating = article.votes_pro.count() - article.votes_con.count()

            data = {
                'response': 'ok',
                'rating': rating,
                'rated_up': article.votes_pro.count(),
                'rated_down': article.votes_con.count(),
            }
            return JResponse(data)

        else:
            data = {
                'response': pgettext('vote_article', 'Нет такой статьи'),
                'header': pgettext('vote_article', 'Оценить статью'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }
            return JResponse(data)

    # если страницу только грузят
    else:
        data = {
            'response': pgettext('core', 'Ошибка типа запроса'),
            'header': pgettext('vote_article', 'Оценить статью'),
            'grey_btn': pgettext('core', 'Закрыть'),
        }
        return JResponse(data)
