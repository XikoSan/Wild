from celery import shared_task

from django_celery_beat.models import PeriodicTask, PeriodicTasks, ClockedSchedule, CrontabSchedule
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
    if party.task is not None:
        party.task.enabled = True
        party.task.save()
    # выключаем праймериз
    Primaries.objects.filter(party=party, running=True).update(running=False, prim_end=timezone.now())
    primaries = Primaries.objects.get(party=party, task__isnull=False)
    # все члены партии
    candidates = Player.objects.filter(party=party)
    # должность лидера партии в данной партии
    party_boss_post = PartyPosition.objects.get(based=True, party=party, party_lead=True)
    # лидером праймериз будет глава партии, если нет голосов
    current_leader = Player.get_instance(party=party, party_post=party_boss_post)
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

    # finish_task = PeriodicTask.objects.get(pk=primaries.task.pk)
    # finish_schedule = CrontabSchedule.objects.get(pk=finish_task.crontab.pk)
    # # if finish_schedule.day_of_week != '*/7':
    # if finish_schedule.hour != '*/2':
    #     # finish_schedule.day_of_week='*/7'
    #     finish_schedule.hour='*/2'
    #     finish_schedule.save()

    task_identificator = primaries.task.id
    # убираем таску у экземпляра модели
    Primaries.objects.select_related('task').filter(party=party, task__isnull=False).update(task=None)
    # удаляем таску
    pt = PeriodicTask.objects.get(pk=task_identificator)
    pt.crontab.delete()

    # schedule, created = CrontabSchedule.objects.get_or_create(
    #     minute='*/7',
    #     hour='*',
    #     day_of_week='*',
    #     day_of_month='*',
    #     month_of_year='*',
    # )
    schedule, created = CrontabSchedule.objects.get_or_create(
        minute=str(timezone.now().now().minute),
        hour=str(timezone.now().now().hour),
        day_of_week='*',
        day_of_month='*/7',
        month_of_year='*',
    )

    primaries.task = PeriodicTask.objects.create(
        name=f'{primaries.party.title}, id {primaries.party.pk} party primaries',
        task='finish_primaries',
        crontab=schedule,
        # clocked=clock,
        # one_off=True,
        args=json.dumps([primaries.party.pk]),
        start_time=timezone.now(),
    )
    primaries.save()


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

    # start_task = PeriodicTask.objects.get(pk=party.task.pk)
    # start_schedule, created = ClockedSchedule.objects.get_or_create(pk=start_task.clocked.pk)
    # start_schedule.clocked_time = timezone.now() + datetime.timedelta(days=7)
    # start_schedule.save()
