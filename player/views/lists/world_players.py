from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from player.views.lists.get_thing_page import get_thing_page
from django.utils.translation import ugettext as _

from player.player import Player
from player.decorators.player import check_player
from party.party import Party


# список всех партий игры
# page - открываемая страница
@login_required(login_url='/')
@check_player
def world_players_list(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    # получаем партии для текущей страницы
    page = request.GET.get('page')
    players = Player.objects.filter(banned=False).order_by('-pk')
    lines = get_thing_page(players, page, 50)

    header = {

        'image': {
            'text': '',
            'select_text': 'Аватар',
            'visible': 'true'
        },

        'nickname': {
            'text': 'Никнейм',
            'select_text': 'Никнейм',
            'visible': 'true'
        },

        'region':{
            'on_map_id':
            {
                'text': '',
                'select_text': 'Герб',
                'visible': 'true'
            },
            'region_name':
            {
                'text': 'Регион',
                'select_text': 'Регион',
                'visible': 'true'
            }
        }
    }

    # отправляем в форму
    return render(request, 'player/redesign/lists/universal_list.html', {
        'page_name': _('Мировое население'),

        'player': player,

        'header': header,
        'lines': lines,
    })
