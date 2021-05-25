from celery import shared_task

from django_celery_beat.models import PeriodicTask, PeriodicTasks, IntervalSchedule

from player.player import Player
from .primaries.primaries import Primaries
from .party import Party
from party.primaries.primaries_bulletin import PrimBulletin
from party.primaries.primaries_leader import PrimariesLeader
from party.position import PartyPosition


# таска выключающая праймериз
@shared_task(name="finish_primaries")
def finish_primaries(party_id):
    party = Party.objects.get(pk=party_id)
    # выключаем праймериз
    primaries = Primaries.objects.filter(party=party).update(running=False)
    primaries = Primaries.objects.get(party=party)
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
        prev_leader = PrimariesLeader.objects.get(party=party)
        prev_leader.delete()
    # назначаем нового лидера праймериз
    leader = PrimariesLeader(party=party, leader=current_leader)
    leader.save()
    # выключаем 24 часовую таску
    if primaries.task:
        primaries.task.enabled = False
        primaries.task.save()


# таска включающая праймериз
@shared_task(name="start_primaries")
def start_primaries(party_id):
    party = Party.objects.select_related('task').prefetch_related('task__interval').only('task__interval__every').get(
        pk=party_id)
    # если интервал таски 7 дней, то увеличиваем до 8 дней
    if party.task.interval.every == 7:
        interval, created = IntervalSchedule.objects.get_or_create(every=8, period=IntervalSchedule.DAYS)
        PeriodicTask.objects.filter(pk=party.task.id).update(interval_id=interval.id)
        PeriodicTasks.changed(party.task)
    # получаем или создаем праймериз и включаем 24 часовую таску
    primaries, created = Primaries.objects.select_related('task').get_or_create(party=party)
    if primaries.task:
        primaries.task.enabled = True
        primaries.task.save()
    primaries.running = True
    primaries.save()
