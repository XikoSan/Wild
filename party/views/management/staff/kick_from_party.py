from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils import timezone

from party.logs.membership_log import MembershipLog
from party.primaries.primaries import Primaries
from party.primaries.primaries_bulletin import PrimBulletin
from player.decorators.player import check_player
from player.player import Player
from player.views.get_subclasses import get_subclasses
from bill.models.bill import Bill
from state.models.parliament.deputy_mandate import DeputyMandate
from gov.models.presidential_voting import PresidentialVoting
from gov.models.president import President
from gov.models.vote import Vote
from gov.models.minister import Minister

# процедура исключения из партии
@login_required(login_url='/')
@check_player
def kick_from_party(request, pk):
    # получаем персонажа
    leader = Player.get_instance(account=request.user)
    # если игрок действительно лидер партии
    if leader.party_post.party_lead:
        # если персонаж с переданным pk принадлежит игроку этой же партии
        if Player.objects.filter(pk=pk, party=leader.party).exists():
            # получаем персонажа, которому надо изменить партию
            kickin_player = Player.get_instance(pk=pk)
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
                    # предварительно получим парламент, из мандата игрока
                    for dm in DeputyMandate.objects.filter(player=kickin_player):

                        parliament = dm.parliament

                        # УБИРАЕМ ЕГО ГОЛОСА ИЗ АКТИВНЫХ ЗП В ПАРЛАМЕНТЕ:
                        bills_classes = get_subclasses(Bill)
                        # для каждого видоа ЗП
                        for bill_class in bills_classes:
                            # если есть активные ЗП этого вида
                            if bill_class.objects.filter(running=True, parliament=parliament).exists():
                                for bill in bill_class.objects.filter(running=True, parliament=parliament):
                                    if kickin_player in bill.votes_pro.all():
                                        bill.votes_pro.remove(kickin_player)

                                    elif kickin_player in bill.votes_con.all():
                                        bill.votes_con.remove(kickin_player)

                        # лишаем его такого счастья
                        mandate = DeputyMandate.objects.get(player=kickin_player)
                        mandate.player = None
                        mandate.save()

                # если персонаж был министром
                if Minister.objects.filter(player=kickin_player).exists():
                    Minister.objects.filter(player=kickin_player).delete()

                # президентские выборы - если был кандидатом
                # если есть гос
                if kickin_player.party.region.state:
                    # если в нем есть президент
                    if President.objects.filter(state=kickin_player.party.region.state).exists():
                        pres = President.objects.get(state=kickin_player.party.region.state)
                        if PresidentialVoting.objects.filter(running=True, president=pres).exists():
                            voting = PresidentialVoting.objects.get(running=True, president=pres)
                            if kickin_player in voting.candidates.all():
                                # удаляем кандидата
                                voting.candidates.remove(kickin_player)
                                voting.save()
                                # если есть голоса за него - удаляем
                                Vote.objects.filter(voting=voting, challenger=kickin_player).delete()


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
