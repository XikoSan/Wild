import random
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player


# главная страница
@login_required(login_url='/')
@check_player
def edu_overview(request):
    player = Player.get_instance(account=request.user)

    assistant_name = ('Ann', pgettext('education', 'Анна'))

    if not player.educated:
        assistant_name = random.choice([
            ('Ann', pgettext('education', 'Анна')),
            ('Lin', pgettext('education', 'Лин')),
            ('Maria', pgettext('education', 'Мария')),
            ('Sofia', pgettext('education', 'София')),
            ('Olga', pgettext('education', 'Ольга'))
        ])

    page = 'education/edu_overview.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name': pgettext('overview', 'Обзор'),
        'player': player,
        'assistant_name': assistant_name,
    })
    return response
