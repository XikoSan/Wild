from celery import shared_task

from django_celery_beat.models import PeriodicTask, PeriodicTasks, ClockedSchedule, CrontabSchedule
import redis
from player.player import Player
from party.primaries.primaries import Primaries
from .party import Party
from django.utils import timezone
import datetime
from party.primaries.primaries_bulletin import PrimBulletin
from party.primaries.primaries_leader import PrimariesLeader
from party.logs.party_apply import PartyApply
from party.position import PartyPosition
from wild_politics.settings import TIME_ZONE
from party.logs.membership_log import MembershipLog


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

    # получаем количество бюллетеней
    bulletins = PrimBulletin.objects.filter(primaries=primaries)
    # если их нет - проверка на роспуск партии
    if bulletins.count() == 0:
        r = redis.StrictRedis(host='redis', port=6379, db=0)
        anyone_online = False
        for char in candidates:
            timestamp = r.hget('online', str(char.pk))
            if timestamp:
                online_dtime = datetime.datetime.fromtimestamp(int(timestamp))
                if not datetime.datetime.now() > datetime.timedelta(days=30) + online_dtime:
                    anyone_online = True
                    break

        if not anyone_online:
            PartyApply.objects.filter(party=party, status='op').update(status='ra')
            # Логировние: меняем запись об партийной активности
            for candidate in candidates:
                MembershipLog.objects.filter(player=candidate, party=party, exit_dtime=None).update(
                    exit_dtime=timezone.now())
            # удаляем партию у всех участников
            candidates.update(party=None, party_post=None)
            # ставим метку удаленной партии
            Party.objects.filter(pk=party.pk).update(deleted=True)
            # снимаем фоновые задачи праймериз этой партии
            if Primaries.objects.filter(party=party.pk, task__isnull=False).exists():
                Primaries.objects.get(party=party.pk, task__isnull=False).delete_task()
                party.delete_task()
            else:
                party.delete_task()
            # на этом всё
            return

    # должность лидера партии в данной партии
    party_boss_post = PartyPosition.objects.get(based=True, party=party, party_lead=True)
    # лидером праймериз будет глава партии, если нет голосов
    current_leader = Player.get_instance(party=party, party_post=party_boss_post)
    current_leader_votes = 0

    # подсчитываем количество голосов за каждого кандидата
    for candidate in candidates:
        votes_num = bulletins.filter(candidate=candidate).count()
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
