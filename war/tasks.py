import datetime

from celery import shared_task
from django.apps import apps
from django.utils import timezone


# раунд войны
@shared_task(name="war_round_task")
def war_round_task(type, id):

    war_class = apps.get_model('war', type)
    war = war_class.objects.get(pk=id)
    war.war_round()


# завершение войны
@shared_task(name="end_war")
def end_war(type, id):

    war_class = apps.get_model('war', type)
    war = war_class.objects.get(pk=id)
    war.war_end()
