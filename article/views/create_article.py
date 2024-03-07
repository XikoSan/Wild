from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from itertools import chain

from player.decorators.player import check_player
from player.player import Player
from article.models.article import Article
from article.forms import NewArticleForm
from wild_politics.settings import JResponse
from django.utils import timezone
import datetime
from django.db import connection


# открыть статью
@login_required(login_url='/')
@check_player
def create_article(request):
    if request.method == "POST":
        player = Player.objects.get(account=request.user)

        # =======================================================================
        # узнаем, может ли игрок дальше постить
        # 0 - 100 кармы = 3 поста в день
        # 100+ кармы = + 1 пост в день
        # 10 постов максимум
        can_post = True

        # сколько уже напощено
        posted_count = Article.objects.filter(player=player,
                                              date__gt=timezone.now() - datetime.timedelta(days=1)).count()

        # сколько кармы. За каждые 100 кармы можно +1 пост в день
        player_articles = Article.objects.only('pk').filter(player=player).values('pk')

        if player_articles:
            articles_tuple = ()

            for article in player_articles:
                articles_tuple += (article['pk'],)

            cursor = connection.cursor()
            cursor.execute(
                "with lines_con as(select count(*) from public.article_article_votes_con where article_id in %s), lines_pro as (select count(*) from public.article_article_votes_pro where article_id in %s) SELECT lines_pro.count - lines_con.count AS difference FROM lines_con, lines_pro;",
                [articles_tuple, articles_tuple])

            carma = cursor.fetchall()[0][0]

        else:
            carma = 0

        limit = 3

        if carma < 0:
            limit = 1

        elif carma > 100:
            limit += carma // 100

            if limit > 10:
                limit = 10

        if posted_count >= limit:
            data = {
                'header': 'Новая статья',
                'grey_btn': 'Закрыть',
                'response': f'Вы достигли ограничения на число статей - {limit} штук',
            }
            return JResponse(data)
        # =======================================================================

        if not request.POST.get('title', ''):
            data = {
                'header': 'Новая статья',
                'grey_btn': 'Закрыть',
                'response': 'Название статьи не должно быть пустым',
            }
            return JResponse(data)

        body = request.POST.get('text', '').replace('script', 'sсript')

        if not body:
            data = {
                'header': 'Новая статья',
                'grey_btn': 'Закрыть',
                'response': 'Текст статьи не должен быть пустым',
            }
            return JResponse(data)

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