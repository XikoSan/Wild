import json
from datetime import datetime
from datetime import timedelta

import pytz
import redis
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.translation import pgettext
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from player.views.lists.get_thing_page import get_thing_page
from region.models.region import Region
from wild_politics.settings import TIME_ZONE
from region.views.lists.get_regions_online import get_region_online
from article.models.article import Article

# список оценивших статью
# page - открываемая страница
@login_required(login_url='/')
@check_player
def article_rated_list(request, pk, mode):
    if not mode == 'likes' and not mode == 'dislikes':
        # перекидываем в список статей
        return redirect("articles")

    # получаем персонажа
    player = Player.get_instance(account=request.user)

    if Article.objects.filter(pk=pk).exists():
        article = Article.objects.get(pk=pk)
    else:
        return redirect('articles')

    # получаем партии для текущей страницы
    page = request.GET.get('page')

    if mode == 'likes':
        players = article.votes_pro.all()

        page_name = pgettext('article', 'Лайкнувшие статью')

    else:
        players = article.votes_con.all()

        page_name = pgettext('article', 'Дизлайкнувшие статью')

    lines = get_thing_page(players, page, 50)

    header = {

        'image': {
            'text': '',
            'select_text': pgettext('lists', 'Аватар'),
            'visible': 'true'
        },

        'nickname': {
            'text': pgettext('lists', 'Никнейм'),
            'select_text': pgettext('lists', 'Никнейм'),
            'visible': 'true'
        },

        'party':{
            'image':
            {
                'text': '',
                'select_text': pgettext('lists', 'Герб'),
                'visible': 'false'
            },
            'title':
            {
                'text': pgettext('lists', 'Партия'),
                'select_text': pgettext('lists', 'Партия'),
                'visible': 'false'
            }
        }
    }

    # отправляем в форму
    return render(request, 'player/redesign/lists/universal_list.html', {
        'page_name': page_name,

        'player': player,

        'header': header,
        'lines': lines,
    })
