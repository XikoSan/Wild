from celery import shared_task

from django_celery_beat.models import PeriodicTask, PeriodicTasks, IntervalSchedule
import datetime

from player.player import Player
from .primaries.primaries import Primaries
from .party import Party
from django.utils import timezone
from party.primaries.primaries_bulletin import PrimBulletin
from party.primaries.primaries_leader import PrimariesLeader
from party.position import PartyPosition


# таска выключающая праймериз
@shared_task(name="finish_primaries")
def finish_primaries(party_id):
    party = Party.objects.get(pk=party_id)

    # выключаем праймериз
    Primaries.objects.filter(party=party, running=True).update(running=False, prim_end=timezone.now())
    primaries = Primaries.objects.get(party=party, task__isnull=False)
    # все члены партии
    candidates = Player.objects.filter(party=party)
    # должность лидера партии в данной партии
    party_boss_post = PartyPosition.objects.get(based=True, party=party, party_lead=True)
    # лидером праймериз будет глава партии, если нет голосов
    current_leader = Player.objects.get(party=party, party_post=party_boss_post)
    current_leader_votes = 0
    # подсчитываем количество голосов за каждого кандидата
    for candidate in candidates:
        votes_num = PrimBulletin.objects.filter(primaries=primaries, candidate=candidate).count()
        if votes_num > current_leader_votes:
            current_leader_votes = votes_num
            current_leader = candidate
    # ищем и удаляем предыдущего лидера праймериз
    if PrimariesLeader.objects.filter(party=party).exists():
        PrimariesLeader.objects.filter(party=party).delete()
    # если нашлась должность лидера с этим человеком - удаляем
    if PrimariesLeader.objects.filter(leader=current_leader).exists():
        PrimariesLeader.objects.filter(leader=current_leader).delete()
    # назначаем нового лидера праймериз
    leader = PrimariesLeader(party=party, leader=current_leader)
    leader.save()

    finish_task = PeriodicTask.objects.get(pk=primaries.task.pk)

    if finish_task.interval.every == 1:
        schedule, created = IntervalSchedule.objects.get_or_create(every=7, period=IntervalSchedule.DAYS)
        # schedule, created = IntervalSchedule.objects.get_or_create(every=7, period=IntervalSchedule.MINUTES)

        finish_task.interval = schedule
        finish_task.save()


# таска включающая праймериз
@shared_task(name="start_primaries")
def start_primaries(party_id):
    party = Party.objects.select_related('task').prefetch_related('task__interval').only('task__interval__every').get(
        pk=party_id)

    # получаем таску из предыдущих праймериз, чтобы переложить в новые
    old_primaries = None
    if Primaries.objects.filter(party=party, task__isnull=False).exists():
        old_primaries = Primaries.objects.select_related('task').get(party=party, task__isnull=False)

    primaries, created = Primaries.objects.select_related('task').get_or_create(party=party,
                                                                                prim_start=timezone.now())

    if old_primaries:
        primaries.task = old_primaries.task
        old_primaries.task = None
        old_primaries.save()

    if primaries.task:
        primaries.task.enabled = True
        primaries.task.save()

    primaries.running = True
    primaries.save()
