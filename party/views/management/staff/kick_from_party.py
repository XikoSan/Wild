from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils import timezone

from party.logs.membership_log import MembershipLog
from party.primaries.primaries import Primaries
from party.primaries.primaries_bulletin import PrimBulletin
from player.decorators.player import check_player
from player.player import Player
from state.models.parliament.deputy_mandate import DeputyMandate


# процедура исключения из партии
@login_required(login_url='/')
@check_player
def kick_from_party(request, pk):
    # получаем персонажа
    leader = Player.objects.get(account=request.user)
    # если игрок действительно лидер партии
    if leader.party_post.party_lead:
        # если персонаж с переданным pk принадлежит игроку этой же партии
        if Player.objects.filter(pk=pk, party=leader.party).exists():
            # получаем персонажа, которому надо изменить партию
            kickin_player = Player.objects.get(pk=pk)
            # если этот игрок - лидер партии
            if kickin_player.party_post.party_lead:
                return redirect('party')
            else:
                # если сейчас идут праймериз:
                if Primaries.objects.filter(running=True, party=kickin_player.party).exists():
                    # и исключаемый уже голосовал:
                    if PrimBulletin.objects.filter(
                            primaries=Primaries.objects.get(running=True, party=kickin_player.party),
                            player=kickin_player).exists():
                        # получить бюллетень праймериз
                        bulletin = PrimBulletin.objects.get(
                            primaries=Primaries.objects.get(running=True, party=kickin_player.party),
                            player=kickin_player)
                        # удаляем бюллетень
                        bulletin.delete()
                    # если есть бюллетени за исключаемого:
                    if PrimBulletin.objects.filter(
                            primaries=Primaries.objects.get(running=True, party=kickin_player.party),
                            candidate=kickin_player).exists():
                        for bultin in PrimBulletin.objects.filter(
                                primaries=Primaries.objects.get(running=True, party=kickin_player.party),
                                candidate=kickin_player):
                            # удаляем все бюллетени за этого игрока
                            bultin.delete()

                # если персонаж был депутатом
                if DeputyMandate.objects.filter(player=kickin_player).exists():
                    # лишаем его такого счастья
                    DeputyMandate.objects.get(player=kickin_player).delete()

                # Логировние: меянем запись об партийной активности
                MembershipLog.objects.filter(player=kickin_player, party=kickin_player.party, exit_dtime=None).update(
                    exit_dtime=timezone.now())
                # Лищаем должностей
                kickin_player.party_post = None
                # задаем его новую партию
                kickin_player.party = None
                # Сохраняем это состояние
                kickin_player.save()
                # Обновляем страницу
                return redirect('party')
        else:
            return redirect('party')
    else:
        return redirect('party')
