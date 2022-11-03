from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from player.views.lists.get_thing_page import get_thing_page
from django.utils.translation import ugettext as _

from player.player import Player
from player.decorators.player import check_player
from party.party import Party

# класс партии, в котором её размер - это поле
class PartyWithSize(Party):
    pk = 0
    size = 0

    class Meta:
        abstract = True

# список всех партий игры
# page - открываемая страница
@login_required(login_url='/')
@check_player
def world_parties_list(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)

    # получаем партии для текущей страницы
    page = request.GET.get('page')
    parties = Party.objects.filter(deleted=False).order_by('foundation_date', 'title')

    parties_with_size = []

    for party in parties:
        size_party = PartyWithSize(
            title = party.title,
            image = party.image,
            region = party.region
        )
        size_party.pk = party.pk,
        size_party.size = Player.objects.filter(party=party).count()

        parties_with_size.append(size_party)

    lines = get_thing_page(parties_with_size, page, 50)

    header = {

        'image': {
            'text': '',
            'select_text': 'Герб',
            'visible': 'true'
        },

        'title': {
            'text': 'Партия',
            'select_text': 'Партия',
            'visible': 'true'
        },

        'size': {
            'text': 'Размер',
            'select_text': 'Размер',
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
        },
    }

    # отправляем в форму
    return render(request, 'player/redesign/lists/universal_list.html', {
        'page_name': _('Партии мира'),

        'player': player,

        'header': header,
        'lines': lines,

    })
