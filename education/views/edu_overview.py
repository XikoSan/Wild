import random
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player
from player.views.overview import overview


def reset_education(request):
    player = Player.get_instance(account=request.user)
    # Ваша проверка условия
    player.educated = False
    player.save()

    return redirect('edu_overview')


def check_and_redirect(request):
    player = Player.get_instance(account=request.user)
    # Ваша проверка условия
    if player.educated:  # Замените `условие` на вашу проверку
        return redirect('overview')  # Перенаправляет на другую страницу при невыполнении условия

    # Если условие выполнено, вызываем 'overview'
    return overview(request)


# главная страница
@login_required(login_url='/')
@check_player
def edu_overview(request):
    player = Player.get_instance(account=request.user)

    if player.educated:  # Замените `условие` на вашу проверку
        return redirect('overview')  # Перенаправляет на другую страницу при невыполнении условия

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
