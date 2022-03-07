import datetime
import operator
from math import floor

import redis
from celery import shared_task
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule, PeriodicTask

from party.party import Party
from player.player import Player
from player.views.get_subclasses import get_subclasses
from bill.models.bill import Bill
from state.models.parliament.bulletin import Bulletin
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament_party import ParliamentParty
from .models.parliament.parliament import Parliament
from .models.parliament.parliament_voting import ParliamentVoting


@shared_task(name="run_bill")
def run_bill(bill_type, bill_pk):
    bills_classes = get_subclasses(Bill)
    bills_dict = {}

    for bill_cl in bills_classes:
        bills_dict[bill_cl.__name__] = bill_cl

    bill = bills_dict[bill_type].objects.get(pk=bill_pk)

    if bill.type:
        # nothing to do here...
        return
    if bill.votes_pro.all().count() > bill.votes_con.all().count():
        bill.do_bill()
    else:
        bills_dict[bill_type].objects.filter(pk=bill_pk).update(running=False, voting_end=timezone.now(), type='rj')

    task_identificator = bill.task.id
    # убираем таску у экземпляра модели
    bills_dict[bill_type].objects.select_related('task').filter(pk=bill_pk).update(task=None)
    # удаляем таску
    PeriodicTask.objects.filter(pk=task_identificator).delete()


@shared_task
def set_mandates(pty_pk, parl_pk, places):
    # все игроки партии-победителя
    players = Player.objects.filter(banned=False, party=Party.objects.get(pk=pty_pk)).order_by('pk')

    # получаем список людей, которые не заходили последнюю неделю
    exclude_list = []
    r = redis.StrictRedis(host='redis', port=6379, db=0)
    # момент завершения выборов - сейчас. Выбираем, чтобы timestamp был одинаков для всех
    timestamp_now = timezone.now().timestamp()

    for char in players:
        timestamp = None
        timestamp = r.hget('online', str(char.pk))
        if timestamp:
            if int(timestamp) < timestamp_now - 604800:
                exclude_list.append(char.pk)
        else:
            exclude_list.append(char.pk)

    # выбираем игроков партии, только тех, кто был последнюю неделю в сети
    players = Player.objects.filter(banned=False, party=Party.objects.get(pk=pty_pk)).exclude(
        pk__in=exclude_list).order_by('pk')

    # # если на всех мест хватает
    # if places > players.count():
    #     places = players.count()

    for num in range(places):

        if num < len(players):
            dm = DeputyMandate(player=players[num], party=Party.objects.get(pk=pty_pk),
                               parliament=Parliament.objects.get(pk=parl_pk))
        else:
            dm = DeputyMandate(player=None, party=Party.objects.get(pk=pty_pk),
                               parliament=Parliament.objects.get(pk=parl_pk))
        dm.save()


# таска выключающая выборы
@shared_task(name="finish_elections")
def finish_elections(parl_id):
    # включаем начало выборов
    parliament = Parliament.objects.get(pk=parl_id)
    if parliament.task is not None:
        parliament.task.enabled = True
        parliament.task.save()
    # выключаем выборы
    ParliamentVoting.objects.filter(parliament=parliament, running=True).update(running=False,
                                                                                voting_end=timezone.now())
    elections = ParliamentVoting.objects.get(parliament=parliament, task__isnull=False)

    # ================================================================
    # находим предыдущие парламентские партии и удаляем их
    if ParliamentParty.objects.filter(parliament=parliament).exists():
        # deleting previous record
        ParliamentParty.objects.filter(parliament=parliament).delete()

    # получаем все голоса на этих выборах
    all_votes_count = Bulletin.objects.filter(voting=elections).count()

    # удаляем депутатские мандаты
    DeputyMandate.objects.filter(parliament=parliament).delete()

    # ищем законы этого парламента
    # bills_types = get_subclasses(Bill)
    # # для каждого типа законопроектов:
    # for type in bills_types:
    #     # если есть активные законы в этом парламенте
    #     if type.objects.filter(parliament=parliament, running=True).exists():
    #         for bill in type.objects.filter(parliament=parliament, running=True):
    #             # снимаем голоса
    #             bill.votes_pro.clear()
    #             bill.votes_con.clear()

    # если есть хоть один голос на выборах:
    if not all_votes_count == 0:
        all_votes = Bulletin.objects.filter(voting=elections)

        # словарь с партиями и количеством голосов за них
        bulltins_dic = {}
        # партии для исключения
        parties_voted = []
        # для каждой партии подсчитываем количество бюллетеней
        for vote in all_votes:
            if vote.party in bulltins_dic:
                bulltins_dic[vote.party] += 1
            else:
                # вносим в словарик
                bulltins_dic[vote.party] = 1
                parties_voted.append(vote.party)

        # количество розданных партийных мест
        seats_gived = 0
        # словарь квот партий
        quates_dic = {}
        # словарь полученных партией мест
        seats_dic = {}
        for spty in parties_voted:
            # изначально заполняется нулями
            seats_dic[spty] = 0
        # пока не розданы все места в парламенте
        while seats_gived < parliament.size:
            # расчет словаря квот каждой партии
            for qpty in parties_voted:
                quates_dic[qpty] = bulltins_dic[qpty] / (2 * seats_dic[qpty] + 1)
            # получаем партию с самой большой квотой
            top_quate = max(quates_dic.items(), key=operator.itemgetter(1))[0]
            # место выдано
            seats_dic[top_quate] = seats_dic[top_quate] + 1
            # увеличиваем счетчик
            seats_gived += 1

        # создаем парламентские партии
        for ppty in parties_voted:
            parliament_pty = ParliamentParty(parliament=parliament, party=ppty,
                                             seats=floor((100 * bulltins_dic[ppty]) / all_votes_count))
            parliament_pty.save()
            # и выдаем мандаты
            set_mandates(ppty.pk, parliament.pk, seats_dic[ppty])

    # ================================================================

    finish_task = PeriodicTask.objects.get(pk=elections.task.pk)
    finish_schedule, created = ClockedSchedule.objects.get_or_create(pk=finish_task.clocked.pk)
    # finish_schedule.clocked_time = timezone.now() + datetime.timedelta(minutes=7)
    finish_schedule.clocked_time = timezone.now() + datetime.timedelta(days=7)
    finish_schedule.save()


# таска включающая выборы
@shared_task(name="start_elections")
def start_elections(parl_id):
    parliament = Parliament.objects.select_related('task').prefetch_related('task__interval').only(
        'task__interval__every').get(
        pk=parl_id)

    # получаем таску из предыдущих праймериз, чтобы переложить в новые
    old_elections = None
    if ParliamentVoting.objects.filter(parliament=parliament, task__isnull=False).exists():
        old_elections = ParliamentVoting.objects.select_related('task').get(parliament=parliament, task__isnull=False)

    parliament_voting, created = ParliamentVoting.objects.select_related('task').get_or_create(parliament=parliament,
                                                                                               voting_start=timezone.now())

    if old_elections:
        parliament_voting.task = old_elections.task
        old_elections.task = None
        old_elections.save()

    if parliament_voting.task:
        parliament_voting.task.enabled = True
        parliament_voting.task.save()

    parliament_voting.running = True
    parliament_voting.save()

    start_task = PeriodicTask.objects.get(pk=parliament.task.pk)

    start_schedule, created = ClockedSchedule.objects.get_or_create(pk=start_task.clocked.pk)
    start_schedule.clocked_time = timezone.now() + datetime.timedelta(days=7)
    # start_schedule.clocked_time = timezone.now() + datetime.timedelta(minutes=7)
    start_schedule.save()
