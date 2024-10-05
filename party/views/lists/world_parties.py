from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import pgettext
from django.utils.translation import ugettext as _

from party.party import Party
from player.decorators.player import check_player
from player.player import Player
from player.views.lists.get_thing_page import get_thing_page


def create_temporary_party_class():
    # класс партии, в котором её размер - это поле
    class _PartyWithSize(Party):
        pk = 0
        size = 0

    return _PartyWithSize


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
        PartyWithSize = create_temporary_party_class()

        size_party = PartyWithSize(
            title=party.title,
            image=party.image,
            region=party.region
        )
        size_party.pk = party.pk,
        # почему-то строкой выше айди складывается в формате (123,)
        size_party.pk = size_party.pk[0]

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

        'region': {
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
        'page_name': pgettext('world_parties', 'Партии мира'),

        'player': player,

        'header': header,
        'lines': lines,

    })
