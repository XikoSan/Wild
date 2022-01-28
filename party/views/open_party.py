from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from party.logs.party_apply import PartyApply
from party.party import Party
from player.decorators.player import check_player
from player.player import Player


@login_required(login_url='/')
@check_player
# Opening page with selected party data
def open_party(request, pk):
    # Получаем объект персонажа, по его ключу
    # Текущий пользователь
    player = Player.objects.get(account=request.user)

    party = get_object_or_404(Party, pk=pk)

    party_characters = Player.objects.only('pk', 'party').filter(party=party)

    return render(request, 'party/party_view.html', {
        'page_name': party.title,
        'player': player,
        'party': party,

        'has_request': PartyApply.objects.filter(player=player, party=party, status='op').exists(),

        'party_characters': party_characters,
        'players_count': party_characters.count(),

    })
