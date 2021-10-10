from celery import shared_task

from player.player import Player


# перелет игрока в другой регион
@shared_task(name="move_to_another_region")
def move_to_another_region(id):
    player = Player.objects.get(pk=id)
    player.region = player.destination
    player.destination = None
    player.task.clocked.delete()
    player.task = None
    player.save()
