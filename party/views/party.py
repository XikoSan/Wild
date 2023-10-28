from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from player.decorators.player import check_player
from player.player import Player
from party.position import PartyPosition, Party


# главная страница
@login_required(login_url='/')
@check_player
def party(request):
    player = Player.get_instance(account=request.user)

    groups = list(player.account.groups.all().values_list('name', flat=True))

    # должности этой партии
    positions = None
    if player.party:
        if player.party_post.party_lead:
            positions = PartyPosition.objects.filter(party=player.party).exclude(party_lead=True)

        elif player.party_post.party_sec:
            positions = PartyPosition.objects.filter(party=player.party).exclude(party_lead=True).exclude(party_sec=True)

    has_open = False
    if not player.educated:
        if Party.objects.filter(deleted=False, type='op').exists():
            has_open = True

    page = 'party/party.html'
    if 'redesign' not in groups:
        page = 'party/redesign/party.html'

    # отправляем в форму
    response = render(request, page, {
        'page_name': _('Партия'),

        'player': player,
        'positions': positions,
        'has_open': has_open,
    })

    # if player_settings:
    #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME, player_settings.language)
    return response
