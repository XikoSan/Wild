import datetime

from celery import shared_task
from django.apps import apps
from django.utils import timezone


# раунд войны
@shared_task(name="war_round_task")
def war_round_task(type, id):

    war_class = apps.get_model('war', type)
    war = war_class.objects.get(pk=id)
    # todo: удалять из редис информацию о уроне сторон боя
    war.war_round()
