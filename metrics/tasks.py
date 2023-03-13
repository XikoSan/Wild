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

    # ----------- деньги -----------
    cash = 0
    if r.exists("daily_cash"):
        cash = int(r.get("daily_cash"))
        r.delete("daily_cash")

    DailyCash.objects.create(
        cash=cash
    )
    # очищаем информацию по регионам
    for region in Region.objects.all():
        if r.exists("daily_cash_" + str(region.pk)):
            r.delete("daily_cash_" + str(region.pk))

    # ----------- нефть -----------
    for oil_type in Region.oil_type_choices:
        oil = 0
        if r.exists("daily_" + oil_type[0]):
            oil = int(float(r.get("daily_" + oil_type[0])))
            r.delete("daily_" + oil_type[0])

        DailyOil.objects.create(
            oil=oil,
            type=oil_type[0]
        )

    # очищаем информацию по регионам
    for region in Region.objects.all():
        for oil_type in Region.oil_type_choices:
            if r.exists("daily_" + str(region.pk) + '_' + oil_type[0]):
                r.delete("daily_" + str(region.pk) + '_' + oil_type[0])

    # ----------- руды -----------
    for mineral in Storage.minerals.keys():
        ore = 0
        if r.exists("daily_" + mineral):
            ore = int(float(r.get("daily_" + mineral)))
            r.delete("daily_" + mineral)

        DailyOre.objects.create(
            ore=ore,
            type=mineral
        )

    # очищаем информацию по регионам
    for region in Region.objects.all():
        for mineral in Storage.minerals.keys():
            if r.exists("daily_" + str(region.pk) + '_' + mineral):
                r.delete("daily_" + str(region.pk) + '_' + mineral)
