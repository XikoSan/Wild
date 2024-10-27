from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import pgettext
from player.views.lists.get_thing_page import get_thing_page
from django.utils.translation import ugettext as _

from region.models.region import Region
from player.player import Player
from player.decorators.player import check_player
from party.party import Party
from party.views.lists.world_parties import create_temporary_party_class

# список всех партий игры
# page - открываемая страница
@login_required(login_url='/')
@check_player
def region_parties_list(request, region_pk):
    # получаем персонажа
    player = Player.get_instance(account=request.user)
    request_region = None

    if Region.objects.filter(pk=region_pk).exists():
        request_region = Region.objects.get(pk=region_pk)
    else:
        return redirect('party')

    # получаем партии для текущей страницы
    page = request.GET.get('page')
    parties = Party.objects.filter(deleted=False, region=request_region).order_by('foundation_date', 'title')

    parties_with_size = []

    for party in parties:

        PartyWithSize = create_temporary_party_class()

        size_party = PartyWithSize(
            title = party.title,
            image = party.image,
            region = party.region
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
            'select_text': pgettext('lists', 'Герб'),
            'visible': 'true'
        },

        'title': {
            'text': pgettext('lists', 'Партия'),
            'select_text': pgettext('lists', 'Партия'),
            'visible': 'true'
        },

        'size': {
            'text': 'Размер',
            'select_text': pgettext('lists', 'Размер'),
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
        },
    }

    # отправляем в форму
    return render(request, 'player/redesign/lists/universal_list.html', {
        'page_name': pgettext('party_top', 'Партии региона'),

        'player': player,

        'header': header,
        'lines': lines,
    })
