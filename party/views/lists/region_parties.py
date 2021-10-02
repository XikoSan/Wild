from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from player.views.lists.get_thing_page import get_thing_page
from django.utils.translation import ugettext as _
from region.region import Region
from player.player import Player
from player.decorators.player import check_player
from party.party import Party


# список всех партий игры
# page - открываемая страница
@login_required(login_url='/')
@check_player
def region_parties_list(request, region_pk):
    # получаем персонажа
    player = Player.objects.get(account=request.user)
    request_region = None

    if Region.objects.filter(pk=region_pk).exists():
        request_region = Region.objects.get(pk=region_pk)
    else:
        return redirect('party')

    # получаем партии для текущей страницы
    page = request.GET.get('page')
    parties = Party.objects.filter(deleted=False, region=request_region).order_by('foundation_date', 'title')
    lines = get_thing_page(parties, page, 50)

    party_sizes = {}
    for party in lines:
        party_sizes[party] = Player.objects.filter(party=party).count()

    # отправляем в форму
    return render(request, 'lists/region_parties_list.html', {
        'page_name': _('Партии региона'),

        'player': player,
        'lines': lines,
        'sizes': party_sizes,

        'request_region': request_region,

        'parties_count': Party.objects.filter(deleted=False, region=request_region).count()})
