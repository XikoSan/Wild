from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils import timezone

from party.logs.membership_log import MembershipLog
from party.party import Party
from party.logs.party_apply import PartyApply
from party.position import PartyPosition
from player.decorators.player import check_player
from player.player import Player


# буферная страница вступления в открытую партию
@login_required(login_url='/')
@check_player
def join_in_party(request, plr_pk, pty_pk):
    # если персонаж с переданным pk принадлежит залогиненному аккаунту
    if Player.objects.filter(pk=plr_pk, account=request.user).exists():
        # получаем персонажа, которому надо изменить партию
        logged_player = Player.objects.get(pk=plr_pk)
        # если игрок - беспартийный
        if not logged_player.party:
            # если партия является открытой
            if Party.objects.get(pk=pty_pk).type == 'op':
                # удаляем все его заявки в другие партии
                PartyApply.objects.filter(player=logged_player).delete()
                # задаем его новую партию
                logged_player.party = Party.objects.get(pk=pty_pk)
                # задаем ему должность нового игрока в партии
                # "базовая должность без лидерки - это 'новичок' "
                party_newbie_post = PartyPosition.objects.get(based=True, party=Party.objects.get(pk=pty_pk),
                                                              party_lead=False)
                logged_player.party_post = party_newbie_post
                # Сохраняем это состояние
                logged_player.save()
                # Логировние: создаем запись о вступлении
                party_log = MembershipLog(player=logged_player, dtime=timezone.now(),
                                          party=Party.objects.get(pk=pty_pk))
                party_log.save()

                # Обновляем страницу
                return redirect('party')
            else:
                return redirect('party')
        else:
            return redirect('party')
    else:
        # Отправляем жулика к ЕГО аккаунтам
        return redirect('party')
