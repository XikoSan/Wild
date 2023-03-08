from celery import shared_task
from django_celery_beat.models import PeriodicTask
import redis
from metrics.models.daily_cash import DailyCash
from metrics.models.daily_oil import DailyOil
from metrics.models.daily_ore import DailyOre
from region.region import Region
from storage.models.storage import Storage

@shared_task(name="save_daily")
def save_daily():
    r = redis.StrictRedis(host='redis', port=6379, db=0)

    cash = 0
    if r.exists("daily_cash"):
        cash = int(r.get("daily_cash"))
        r.delete("daily_cash")

    DailyCash.objects.create(
        cash=cash
    )

    for oil_type in Region.oil_type_choices:
        oil = 0
        if r.exists("daily_" + oil_type[0]):
            oil = int(float(r.get("daily_" + oil_type[0])))
            r.delete("daily_" + oil_type[0])

        DailyOil.objects.create(
            oil=oil,
            type=oil_type[0]
        )

    for mineral in Storage.minerals.keys():
        ore = 0
        if r.exists("daily_" + mineral):
            ore = int(float(r.get("daily_" + mineral)))
            r.delete("daily_" + mineral)

        DailyOre.objects.create(
            ore=ore,
            type=mineral
        )
