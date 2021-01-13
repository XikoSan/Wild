from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from party.party import Party
from party.logs.party_apply import PartyApply
from player.decorators.player import check_player
from player.player import Player


# буферная страница изменения типа партии
@login_required(login_url='/')
@check_player
def switch_party_type(request):
    # получаем персонажа
    player = Player.objects.get(account=request.user)

    if player.party_post:
        # если игрок действительно лидер партии
        if player.party_post.party_lead:

            changing_party = Party.objects.get(pk=player.party.pk)

            # если партия открытая - сделать частной
            if changing_party.type == 'op':
                changing_party.type = 'pt'
                changing_party.save()
                return redirect('party')

            # если партия частная - открыть
            elif changing_party.type == 'pt':
                changing_party.type = 'op'
                changing_party.save()
                # если в партию были заявки - отклонить все
                PartyApply.objects.filter(party=changing_party, status='op').update(status='ra')
                return redirect('party')
            else:
                return redirect('party')
        else:
            return redirect('party')
    else:
        return redirect('party')
