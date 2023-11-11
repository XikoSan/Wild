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
from datetime import timedelta
from wild_politics.settings import TIME_ZONE
from party.logs.membership_log import MembershipLog
from datetime import time
from django.db.models import Q


# таска, создающая другие фоновые задачи за 12 часов:
# - задачи праймериз
# - задачи выборов
# - задачи през выборов
@shared_task(name="tasks_observer")
def tasks_observer():

    from player.logs.print_log import log

    # получаем текущее время
    current_day = datetime.datetime.now().weekday()

    start_time = datetime.datetime.now().time()
    end_time = (datetime.datetime.combine(datetime.datetime.min, start_time) + timedelta(hours=1)).time()

    # start_time = time(13, 0)  # начальное время интервала (21:00)
    # end_time = time(13, 59)  # конечное время интервала (22:00)

    log(current_day)
    log(start_time)
    log(end_time)

    # задачи начала праймериз:
    # получаем партии, день недели и час начала праймериз которых совпадают с текущим
    parties = Party.objects.filter(
                                    Q(primaries_day=current_day)
                                    & Q(foundation_date__time__gte=start_time)
                                    & Q(foundation_date__time__lt=end_time)
                                   )
    log(parties)
    # для каждой партии:
    for party in parties:
    # если минута совпадает с текущей - стартовать праймериз прямо сейчас
        if party.foundation_date.minute == timezone.now().minute:
            start_primaries(party.pk)

    # иначе - создаём таску старта праймериз
        else:
            party.setup_task()


    # задачи завершения праймериз:
    # получаем партии, день недели праймериз которых был вчера, а час совпадают с текущим
    if current_day == 0:
        current_day = 6
    else:
        current_day -= 1

    log(current_day)
    log(start_time)
    log(end_time)

    parties = Party.objects.filter(
                                    Q(primaries_day=current_day) &
                                    Q(foundation_date__time__gte=start_time) &
                                    Q(foundation_date__time__lt=end_time)
                                   )
    log(f'завершение: {parties}')

    for party in parties:
    # если минута совпадает с текущей - завершить праймериз прямо сейчас
        if party.foundation_date.minute == timezone.now().minute:
            finish_primaries(party.pk)
    # иначе - создаём таску завершения праймериз
        else:
            if Primaries.objects.filter(party=party, running=True).exists():
                primaries = Primaries.objects.get(party=party, running=True)
                primaries.setup_task()


# таска выключающая праймериз
@shared_task(name="finish_primaries")
def finish_primaries(party_id):
    # если партии нет - выходим, а не падаем
    if not Party.objects.filter(pk=party_id).exists():
        return
    party = Party.objects.get(pk=party_id)

    # выключаем праймериз
    primaries = Primaries.objects.get(party=party, running=True)

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

    primaries.running = False
    primaries.prim_end = timezone.now()

    task_id = None
    if primaries.task:
        task_id = primaries.task.pk
        primaries.task = None

    primaries.save()

    if task_id:
        PeriodicTask.objects.filter(pk=task_id).delete()




# таска включающая праймериз
@shared_task(name="start_primaries")
def start_primaries(party_id):
    party = Party.objects.select_related('task').prefetch_related('task__interval').only('task__interval__every').get(
        pk=party_id)

    Primaries.objects.select_related('task').get_or_create(party=party, prim_start=timezone.now())

    if party.task:
        task_id = party.task.pk
        party.task = None
        party.save()

        PeriodicTask.objects.filter(pk=task_id).delete()
