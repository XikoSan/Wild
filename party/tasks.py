from celery import shared_task
from .primaries.primaries import Primaries
from .party import Party

# таска выключающая праймериз
@shared_task(name="finish_primaries")
def finish_primaries(party_id):
    party = Party.objects.get(pk=party_id)
    primaries = Primaries.objects.filter(party=party).update(running=False)
    primaries = Primaries.objects.get(party=party)
    if primaries.task:
        primaries.task.enabled = False
        primaries.task.save()

# таска включающая праймериз
@shared_task(name="start_primaries")
def start_primaries(party_id):
    party = Party.objects.get(pk=party_id)
    primaries, created = Primaries.objects.get_or_create(party=party)
    if primaries.task:
        primaries.task.enabled = True
        primaries.task.save()
    primaries.running = True
    primaries.save()


