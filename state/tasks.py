import datetime
import operator
import redis
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule, PeriodicTask, CrontabSchedule
from math import floor
from datetime import timedelta
from bill.models.bill import Bill
from gov.models.minister import Minister
from gov.models.president import President
from gov.models.presidential_voting import PresidentialVoting
from gov.models.vote import Vote
from party.party import Party
from party.primaries.primaries_leader import PrimariesLeader
from player.player import Player
from player.views.get_subclasses import get_subclasses
from region.models.region import Region
from state.models.parliament.bulletin import Bulletin
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament_party import ParliamentParty
from .models.parliament.parliament import Parliament
from .models.parliament.parliament_voting import ParliamentVoting


@shared_task(name="run_bill")
@transaction.atomic
def run_bill(bill_type, bill_pk):
    bills_classes = get_subclasses(Bill)
    bills_dict = {}

    for bill_cl in bills_classes:
        bills_dict[bill_cl.__name__] = bill_cl

    bill = bills_dict[bill_type].objects.get(pk=bill_pk)

    if bill.type:
        # nothing to do here...
        return

    if bill.votes_pro.count() == bill.votes_con.count() == 0:
        bills_dict[bill_type].objects.filter(pk=bill_pk).update(running=False, voting_end=timezone.now(), type='rj')

    else:
        # считаем процент голосов за
        pro_percent = bill.votes_pro.count() * 100 / (bill.votes_pro.count() + bill.votes_con.count())
        # если голосов "за" больше, и процент голосов больше порога
        if bill.votes_pro.all().count() > bill.votes_con.all().count() \
                and pro_percent > bill.acceptation_percent:
            bill.do_bill()
        else:
            bills_dict[bill_type].objects.filter(pk=bill_pk).update(running=False, voting_end=timezone.now(), type='rj')

    task_identificator = bill.task.id
    # убираем таску у экземпляра модели
    bills_dict[bill_type].objects.select_related('task').filter(pk=bill_pk).update(task=None)
    # удаляем таску
    PeriodicTask.objects.filter(pk=task_identificator).delete()


@shared_task
@transaction.atomic
def set_mandates(pty_pk, parl_pk, places):
    lv_places = places
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

    # выбираем министров от этой партии
    party_ministers = Minister.objects.filter(player__in=players)

    # если есть министры, которые неактивны - удаляем их
    if party_ministers.filter(player__pk__in=exclude_list).exists():
        party_ministers.filter(player__pk__in=exclude_list).delete()
        # и обновляем список
        party_ministers = Minister.objects.filter(player__in=players)

    # если у нас остались министры - выдадим им в первую очередь
    if party_ministers:
        for minister in party_ministers:
            # удалим их из общего списка, чтобы не получили два мандата
            players = players.exclude(pk=minister.player.pk)

            if lv_places > 0:
                # если у данного игрока есть мандат президента (в этом госе или где-то ещё)
                if DeputyMandate.objects.filter(player=minister.player, is_president=True).exists():
                    dm = DeputyMandate(player=None, party=Party.objects.get(pk=pty_pk),
                                       parliament=Parliament.objects.get(pk=parl_pk))
                else:
                    dm = DeputyMandate(player=minister.player, party=Party.objects.get(pk=pty_pk),
                                       parliament=Parliament.objects.get(pk=parl_pk))
                dm.save()
                lv_places -= 1

    for num in range(lv_places):

        if num < len(players):
            # если у данного игрока есть мандат президента (в этом госе или где-то ещё)
            if DeputyMandate.objects.filter(player=players[num], is_president=True).exists():
                dm = DeputyMandate(player=None, party=Party.objects.get(pk=pty_pk),
                                   parliament=Parliament.objects.get(pk=parl_pk))
            else:
                dm = DeputyMandate(player=players[num], party=Party.objects.get(pk=pty_pk),
                                   parliament=Parliament.objects.get(pk=parl_pk))
        else:
            dm = DeputyMandate(player=None, party=Party.objects.get(pk=pty_pk),
                               parliament=Parliament.objects.get(pk=parl_pk))
        dm.save()


# таска выключающая выборы
@shared_task(name="finish_elections")
@transaction.atomic
def finish_elections(parl_id):
    # включаем начало выборов
    parliament = Parliament.objects.get(pk=parl_id)
    if parliament.task is not None:
        parliament.task.enabled = True
        parliament.task.save()
    # выключаем выборы
    ParliamentVoting.objects.filter(parliament=parliament, running=True).update(running=False,
                                                                                voting_end=timezone.now())

    if ParliamentVoting.objects.filter(parliament=parliament, task__isnull=False).exists():
        elections = ParliamentVoting.objects.get(parliament=parliament, task__isnull=False)
    else:
        return

    # ================================================================
    # находим предыдущие парламентские партии и удаляем их
    if ParliamentParty.objects.filter(parliament=parliament).exists():
        # deleting previous record
        ParliamentParty.objects.filter(parliament=parliament).delete()

    # получаем все голоса на этих выборах
    all_votes_count = Bulletin.objects.filter(voting=elections).count()

    # удаляем депутатские мандаты
    DeputyMandate.objects.filter(parliament=parliament, is_president=False).delete()

    # ищем законы этого парламента
    bills_types = get_subclasses(Bill)
    # для каждого типа законопроектов:
    for type in bills_types:
        # если есть активные законы в этом парламенте
        if type.objects.filter(parliament=parliament, running=True).exists():
            for bill in type.objects.filter(parliament=parliament, running=True):
                # снимаем голоса
                bill.votes_pro.clear()
                bill.votes_con.clear()

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

        # удаляем министров, не получивших мандаты
        players_deputates = []
        for dm in DeputyMandate.objects.filter(parliament=parliament.pk):
            players_deputates.append(dm.player)

        Minister.objects.filter(state=parliament.state).exclude(player__in=players_deputates).delete()

    task_id = None
    if elections.task:
        task_id = elections.task.pk
        elections.task = None

    elections.save()

    if task_id:
        PeriodicTask.objects.filter(pk=task_id).delete()


# таска включающая выборы
@shared_task(name="start_elections")
@transaction.atomic
def start_elections(parl_id):
    parliament = Parliament.objects.select_related('task').prefetch_related('task__interval').only(
        'task__interval__every').get(
        pk=parl_id)

    # если в этом часу уже запускали выборы
    if ParliamentVoting.objects.filter(parliament=parliament, voting_start__gt=timezone.now() - timedelta(hours=1)).exists():
        return

    parliament_voting, created = ParliamentVoting.objects.select_related('task').get_or_create(parliament=parliament,
                                                                                               voting_start=timezone.now())
    parliament_voting.running = True

    if parliament.task:
        task_id = parliament.task.pk
        parliament.task = None
        parliament.save()

        PeriodicTask.objects.filter(pk=task_id).delete()


# таска выключающая выборы
@shared_task(name="finish_presidential")
@transaction.atomic
def finish_presidential(pres_id):
    # если президента нет - выходим
    if not President.objects.filter(pk=pres_id).exists():
        return
    # включаем начало выборов
    president = President.objects.get(pk=pres_id)

    # выключаем выборы
    PresidentialVoting.objects.filter(president=president, running=True).update(running=False,
                                                                                voting_end=timezone.now())

    if PresidentialVoting.objects.filter(president=president, task__isnull=False).exists():
        elections = PresidentialVoting.objects.get(president=president, task__isnull=False)
    else:
        return

        # ================================================================

    # получаем все голоса на этих выборах
    all_votes_count = Vote.objects.filter(voting=elections).count()

    # если есть хоть один голос на выборах:
    if not all_votes_count == 0:
        all_votes = Vote.objects.filter(voting=elections)

        # словарь с кандидатами и количеством голосов за них
        bulltins_dic = {}
        # список людей, за которых есть голоса
        challengers_with_vote = []
        # для каждой партии подсчитываем количество бюллетеней
        for vote in all_votes:
            if vote.challenger in bulltins_dic:
                bulltins_dic[vote.challenger] += 1
            else:
                # вносим в словарик
                bulltins_dic[vote.challenger] = 1
                challengers_with_vote.append(vote.challenger)

        r = redis.StrictRedis(host='redis', port=6379, db=0)
        timestamp_now = timezone.now().timestamp()

        max_votes = 0
        max_cadidate = president.leader

        for candidate in challengers_with_vote:
            if bulltins_dic[candidate] > max_votes:

                timestamp = r.hget('online', str(candidate.pk))

                if timestamp:
                    if int(timestamp) < timestamp_now - 604800:
                        continue
                else:
                    continue

                max_votes = bulltins_dic[candidate]
                max_cadidate = candidate

        president.leader = max_cadidate
        president.save()

        # если есть парламент
        if Parliament.objects.filter(state=president.state).exists():
            # добавляем президента в новое место в парламенте
            parl = Parliament.objects.get(state=president.state)
            # если у нового президента есть мандат - очищаем его
            if DeputyMandate.objects.filter(player=max_cadidate).exists():
                DeputyMandate.objects.filter(player=max_cadidate).update(player=None)
            # если у нового президента есть министерское место - очищаем его
            if Minister.objects.filter(player=max_cadidate).exists():
                Minister.objects.filter(player=max_cadidate).delete()
            # ищем прездидентское место
            if DeputyMandate.objects.filter(parliament=parl, is_president=True).exists():
                DeputyMandate.objects.filter(parliament=parl, is_president=True).update(player=max_cadidate)

    task_id = None
    if elections.task:
        task_id = elections.task.pk
        elections.task = None

    elections.save()

    if task_id:
        PeriodicTask.objects.filter(pk=task_id).delete()


# таска включающая президентские выборы
@shared_task(name="start_presidential")
@transaction.atomic
def start_presidential(pres_id):
    president = President.objects.select_related('task').prefetch_related('task__interval').only(
        'task__interval__every').get(
        pk=pres_id)

    # если в этом часу уже запускали выборы
    if PresidentialVoting.objects.filter(president=president, voting_start__gt=timezone.now() - timedelta(hours=1)).exists():
        return

    voting, created = PresidentialVoting.objects.select_related('task').get_or_create(president=president,
                                                                                      voting_start=timezone.now())

    prim_leaders = PrimariesLeader.objects.filter(
        party__in=Party.objects.filter(deleted=False, region__in=Region.objects.filter(state=president.state)))

    r = redis.StrictRedis(host='redis', port=6379, db=0)
    timestamp_now = timezone.now().timestamp()

    for prim_leader in prim_leaders:

        timestamp = r.hget('online', str(prim_leader.leader.pk))

        if timestamp:
            if int(timestamp) < timestamp_now - 604800:
                continue
        else:
            continue

        voting.candidates.add(prim_leader.leader)

    voting.save()

    task_id = None
    if president.task:
        task_id = president.task.pk
        president.task = None

    president.save()

    if task_id:
        PeriodicTask.objects.filter(pk=task_id).delete()
