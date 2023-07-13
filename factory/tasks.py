from celery import shared_task

from player.player import Player
from factory.models.auto_produce import AutoProduce
from django.utils import timezone


# сбор есст. прироста раз в десять минут
@shared_task(name="good_produce")
def good_produce(id):

    AutoProduce.objects.get(pk=id).produce_good()
