from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from player.views.lists.get_thing_page import get_thing_page
from django.utils.translation import ugettext as _
from django.utils.translation import pgettext
from region.models.region import Region
from player.player import Player
from player.decorators.player import check_player
from party.party import Party


# список пропиисанных в регионе
# page - открываемая страница
@login_required(login_url='/')
@check_player
def region_citizens_list(request, region_pk):
    # получаем персонажа
    player = Player.get_instance(account=request.user)
    request_region = None

    if Region.objects.filter(pk=region_pk).exists():
        request_region = Region.objects.get(pk=region_pk)
    else:
        return redirect('party')

    # получаем партии для текущей страницы
    page = request.GET.get('page')
    players = Player.objects.filter(banned=False, residency=request_region).order_by('-residency_date')
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
        'page_name': pgettext('lists', 'Граждане региона'),

        'player': player,

        'header': header,
        'lines': lines,
    })
