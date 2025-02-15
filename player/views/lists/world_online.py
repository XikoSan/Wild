from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _
from django.utils.translation import pgettext

from player.decorators.player import check_player
from player.player import Player
from player.views.lists.get_thing_page import get_thing_page
from region.models.region import Region
from region.views.lists.get_regions_online import get_region_online


# список всех партий игры
# page - открываемая страница
@login_required(login_url='/')
@check_player
def world_online_list(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    # получаем игроков для текущей страницы
    page = request.GET.get('page')

    all_regions = Region.objects.only('pk').all()
    # список айди игроков
    chars_pk_list = []

    for region in all_regions:
        dummy, dummy2, players_online = get_region_online(region)

        for char_pk in players_online:
            chars_pk_list.append(char_pk)

    players = Player.objects.filter(banned=False, pk__in=chars_pk_list).order_by('-pk')

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

        'region': {
            'on_map_id':
                {
                    'text': '',
                    'select_text': pgettext('lists', 'Герб'),
                    'visible': 'true'
                },
            'region_name':
                {
                    'text': pgettext('lists', 'Регион'),
                    'select_text': pgettext('lists', 'Регион'),
                    'visible': 'true'
                }
        }
    }

    # отправляем в форму
    return render(request, 'player/redesign/lists/universal_list.html', {
        'page_name': pgettext('lists', 'Мировой онлайн'),

        'player': player,

        'header': header,
        'lines': lines,
    })
