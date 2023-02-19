# from celery import uuid
# from celery.task.control import revoke
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone

from party.logs.membership_log import MembershipLog
from party.party import Party
from party.primaries.primaries import Primaries
from party.primaries.primaries_bulletin import PrimBulletin
from party.views.management.staff.reject_all_requests import reject_all_requests
from player.decorators.player import check_player
from player.player import Player
from player.views.get_subclasses import get_subclasses
from bill.models.bill import Bill
from state.models.parliament.deputy_mandate import DeputyMandate


# буферная страница выхода из партии
@login_required(login_url='/')
@check_player
def leave_party(request):
    # получаем персонажа
    player = Player.get_instance(account=request.user)
    # if player.party == Party.objects.get(pk=party_id):
    if player.party == Party.objects.get(pk=request.POST.get('party_id')):
        # если этот игрок - лидер партии
        if player.party_post.party_lead:
            # если в клане больше одного человека (то есть не только глава)
            # if Player.objects.filter(party=Party.objects.get(pk=party_id)).count() > 1:
            if Player.objects.filter(party=Party.objects.get(pk=request.POST.get('party_id'))).count() > 1:
                data = {
                    'response': 'Вы не исключили всех однопартийев',
                }
                return JsonResponse(data)
            # предварительно получаем партию для удаления
            party = Party.objects.get(pk=player.party.pk)
            # если сейчас идут праймериз:
            if Primaries.objects.filter(running=True, party=player.party).exists():
                # и уходящий уже голосовал:
                if PrimBulletin.objects.filter(primaries=Primaries.objects.get(running=True, party=player.party),
                                               player=player).exists():
                    # получить бюллетень праймериз
                    bulletin = PrimBulletin.objects.get(
                        primaries=Primaries.objects.get(running=True, party=player.party),
                        player=player)
                    # удаляем бюллетень
                    bulletin.delete()
                # если есть бюллетени за уходящего:
                if PrimBulletin.objects.filter(primaries=Primaries.objects.get(running=True, party=player.party),
                                               candidate=player).exists():
                    for bultin in PrimBulletin.objects.filter(
                            primaries=Primaries.objects.get(running=True, party=player.party),
                            candidate=player):
                        # удаляем все бюллетени за этого игрока
                        bultin.delete()

            # если партия состояла в парламенте
            if DeputyMandate.objects.filter(party=player.party).exists():
                # если глава сам был депутатом
                if DeputyMandate.objects.filter(party=player.party, player=player).exists():
                    # предварительно получим парламент, из мандата игрока
                    parliament = DeputyMandate.objects.get(party=player.party, player=player).parliament

                    # УБИРАЕМ ЕГО ГОЛОСА ИЗ АКТИВНЫХ ЗП В ПАРЛАМЕНТЕ:
                    bills_classes = get_subclasses(Bill)
                    # для каждого видоа ЗП
                    for bill_class in bills_classes:
                        # если есть активные ЗП этого вида
                        if bill_class.objects.filter(running=True, parliament=parliament).exists():
                            for bill in bill_class.objects.filter(running=True, parliament=parliament):
                                if player in bill.votes_pro.all():
                                    bill.votes_pro.remove(player)

                                elif player in bill.votes_con.all():
                                    bill.votes_con.remove(player)

                # лишаем его такого счастья
                DeputyMandate.objects.filter(party=player.party).update(player=None)

            # отклоняем все заявки в партию
            reject_all_requests(request)
            # Лищаем должностей
            player.party_post = None
            # Логировние: меянем запись об партийной активности
            MembershipLog.objects.filter(player=player, party=player.party, exit_dtime=None).update(
                exit_dtime=timezone.now())
            # задаем его новую партию
            player.party = None
            # Сохраняем это состояние
            player.save()
            # удаляем партию
            Party.objects.filter(pk=party.pk).update(deleted=True)
            # снимаем фоновые задачи праймериз этой партии
            if Primaries.objects.filter(party=party.pk, task__isnull=False).exists():
                Primaries.objects.get(party=party.pk, task__isnull=False).delete_task()
                party.delete_task()
            else:
                party.delete_task()
            # revoke(Party.objects.get(pk=party.pk).task_id, terminate=True)
            # Обновляем страницу
            data = {
                'response': 'ok',
            }
            return JsonResponse(data)
        else:
            # если сейчас идут праймериз:
            if Primaries.objects.filter(running=True, party=player.party).exists():
                # и уходящий уже голосовал:
                if PrimBulletin.objects.filter(primaries=Primaries.objects.get(running=True, party=player.party),
                                               player=player).exists():
                    # получить бюллетень праймериз
                    bulletin = PrimBulletin.objects.get(
                        primaries=Primaries.objects.get(running=True, party=player.party),
                        player=player)
                    # удаляем бюллетень
                    bulletin.delete()
                # если есть бюллетени за уходящего:
                if PrimBulletin.objects.filter(primaries=Primaries.objects.get(running=True, party=player.party),
                                               candidate=player).exists():
                    for bultin in PrimBulletin.objects.filter(
                            primaries=Primaries.objects.get(running=True, party=player.party),
                            candidate=player):
                        # удаляем все бюллетени за этого игрока
                        bultin.delete()

            # если персонаж был депутатом
            if DeputyMandate.objects.filter(player=player).exists():
                # предварительно получим парламент, из мандата игрока
                parliament = DeputyMandate.objects.get(player=player).parliament

                # УБИРАЕМ ЕГО ГОЛОСА ИЗ АКТИВНЫХ ЗП В ПАРЛАМЕНТЕ:
                bills_classes = get_subclasses(Bill)
                # для каждого видоа ЗП
                for bill_class in bills_classes:
                    # если есть активные ЗП этого вида
                    if bill_class.objects.filter(running=True, parliament=parliament).exists():
                        for bill in bill_class.objects.filter(running=True, parliament=parliament):
                            if player in bill.votes_pro.all():
                                bill.votes_pro.remove(player)

                            elif player in bill.votes_con.all():
                                bill.votes_con.remove(player)

                # лишаем его такого счастья
                mandate = DeputyMandate.objects.get(player=player)
                mandate.player = None
                mandate.save()

            # Логировние: меянем запись об партийной активности
            MembershipLog.objects.filter(player=player, party=player.party, exit_dtime=None).update(
                exit_dtime=timezone.now())
            # Лищаем должностей
            player.party_post = None
            # задаем его новую партию
            player.party = None
            # Сохраняем это состояние
            player.save()
            data = {
                'response': 'ok',
            }
            return JsonResponse(data)
    else:
        data = {
            'response': 'Вы пытаетесь покинуть чужую партию. Это как вообще?',
        }
        return JsonResponse(data)
