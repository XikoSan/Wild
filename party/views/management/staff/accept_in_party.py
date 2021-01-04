from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils import timezone

from party.logs.membership_log import MembershipLog
from party.party import Party
from party.party_apply import PartyApply
from party.position import PartyPosition
from player.decorators.player import check_player
from player.player import Player


# буферная страница принтия в частную партию
@login_required(login_url='/')
@check_player
def accept_in_party(request, plr_pk):
    # получаем персонажа
    player = Player.objects.get(account=request.user)
    if player.party_post:
        # если игрок действительно лидер партии или хотя бы секретарь
        if player.party_post.party_lead or player.party_post.party_sec:
            # получаем персонажа, которому надо изменить партию
            accepted_player = Player.objects.get(pk=plr_pk)
            # удаляем все его заявки в другие партии
            PartyApply.objects.filter(player=accepted_player).delete()
            # задаем его новую партию
            accepted_player.party = player.party
            # задаем ему должность нового игрока в партии
            # "базовая должность без лидерки - это 'новичок' "
            party_newbie_post = PartyPosition.objects.get(based=True, party=player.party,
                                                          party_lead=False)
            accepted_player.party_post = party_newbie_post
            # Сохраняем это состояние
            accepted_player.save()

            # Логировние: создаем запись о вступлении
            party_log = MembershipLog(player=accepted_player, dtime=timezone.now(),
                                      party=player.party)
            party_log.save()

            return redirect('party_requests')
        else:
            return redirect('party')
    else:
        return redirect('party')
