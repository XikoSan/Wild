from celery import shared_task

from player.player import Player
from player.logs.auto_mining import AutoMining

# перелет игрока в другой регион
@shared_task(name="move_to_another_region")
def move_to_another_region(id):
    player = Player.get_instance(pk=id)
    player.region = player.destination
    player.destination = None
    player.task.clocked.delete()
    player.task = None
    player.save()
    player.increase_calc()


# сбор есст. прироста раз в десять минут
@shared_task(name="crude_retrieve")
def crude_retrieve(id):

    AutoMining.objects.get(pk=id).retrieve_crude()
