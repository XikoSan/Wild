from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from party.party import Party
from party.party_apply import PartyApply
from player.decorators.player import check_player
from player.player import Player


# отклонить все заявки
@login_required(login_url='/')
@check_player
def dismiss_all_requests(request):
    # получаем персонажа
    player = Player.objects.get(account=request.user)
    if player.party_post:
        # если игрок действительно лидер партии или хотя бы секретарь
        if player.party_post.party_lead or player.party_post.party_sec:
            # удаляем все заявки в эту партию
            PartyApply.objects.filter(party=player.party).delete()
        return redirect('party')
    else:
        return redirect('party')
