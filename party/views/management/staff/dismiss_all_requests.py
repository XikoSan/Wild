from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from party.party import Party
from party.party_apply import PartyApply
from player.decorators.player import check_player


# отклонить все заявки
@login_required(login_url='/')
@check_player
def dismiss_all_requests(request, pty_pk):
    # получаем персонажа
    player = Player.objects.get(account=request.user)
    # если игрок действительно лидер партии или хотя бы секретарь
    if player.party_post.party_lead or player.party_post.party_sec:
        # если партия с переданным pk псуществует
        # а также существует партия лидера партии (а вдруг)
        if Party.objects.filter(pk=pty_pk).exists() and Party.objects.filter(pk=player.party.pk).exists():
            # если это одна и та же партия
            if Party.objects.get(pk=pty_pk) == Party.objects.get(pk=player.party.pk):
                # удаляем все заявки в эту партию
                PartyApply.objects.filter(party=Party.objects.get(pk=pty_pk)).delete()
                return redirect('party', pty_pk)
                # return redirect('party_requests', pty_pk)
            else:
                return redirect('party')
        else:
            return redirect('party')
    else:
        return redirect('party')
