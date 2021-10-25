from celery import shared_task

from django.apps import apps


# раунд войны
@shared_task(name="war_round_task")
def war_round_task(type, id):
    war_class = apps.get_model('war', type)
    war_class.objects.get(pk=id).war_round()
