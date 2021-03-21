import time

from celery import shared_task

from player.player import Player
from region.region import Region


@shared_task
def move_to_another_region(id, destination, duration):
    # time.sleep(int(float(duration)) * 60)
    time.sleep(5)
    player = Player.objects.get(pk=id)
    player.destination = None
    player.region = Region.objects.get(on_map_id=destination)
    player.save()