from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from party.party import Party
from party.logs.party_apply import PartyApply
from player.decorators.player import check_player
from player.player import Player


# буферная страница подачи заявки в партию
@login_required(login_url='/')
@check_player
def request_in_party(request, plr_pk, pty_pk):
    # если персонаж с переданным pk принадлежит залогиненному аккаунту
    if Player.objects.filter(pk=plr_pk, account=request.user).exists():
        # получаем персонажа, которому надо изменить партию
        logged_player = Player.objects.get(pk=plr_pk)
        new_req = PartyApply(party=Party.objects.get(pk=pty_pk), player=logged_player)
        new_req.save()
        return redirect('party')
    else:
        # Отправляем жулика к ЕГО аккаунтам
        return redirect('party')
