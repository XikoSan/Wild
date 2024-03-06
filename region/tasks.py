import json
from celery import shared_task, current_app
from django.utils import timezone
from django_celery_beat.models import PeriodicTask

from player.logs.auto_mining import AutoMining
from player.player import Player


# перелет игрока в другой регион
@shared_task(name="move_to_another_region")
def move_to_another_region(id):
    player = Player.get_instance(pk=id)
    player.region = player.destination
    player.destination = None
    player.arrival = timezone.now()
    player.task.clocked.delete()
    player.task = None
    player.save()
    player.increase_calc()


# сбор есст. прироста раз в десять минут
@shared_task(name="crude_retrieve")
def crude_retrieve(id):
    if AutoMining.objects.filter(pk=id).exists():
        AutoMining.objects.get(pk=id).retrieve_crude()
    else:
        PeriodicTask.objects.filter(task="crude_retrieve", args=json.dumps([id])).delete()
