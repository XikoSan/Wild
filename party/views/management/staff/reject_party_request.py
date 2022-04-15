from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from party.party import Party
from party.logs.party_apply import PartyApply
from player.decorators.player import check_player
from player.player import Player


# буферная страница принтия в частную партию
@login_required(login_url='/')
@check_player
def reject_party_request(request, plr_pk):
    # получаем персонажа
    player = Player.get_instance(account=request.user)
    # если игрок действительно лидер партии или хотя бы секретарь
    if player.party_post:
        if player.party_post.party_lead or player.party_post.party_sec:
            # получаем персонажа, чью заявку мы отклоняем
            accepted_player = Player.get_instance(pk=plr_pk)
            # удаляем его заявку
            PartyApply.objects.filter(player=accepted_player, party=player.party, status='op').update(
                status='rj')
            return redirect('party_requests')
        else:
            return redirect('party')
    else:
        return redirect('party')
