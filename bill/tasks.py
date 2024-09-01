from celery import shared_task
from django_celery_beat.models import PeriodicTask
import redis
from metrics.models.daily_cash import DailyCash
from metrics.models.daily_oil import DailyOil
from metrics.models.daily_ore import DailyOre
from region.models.region import Region
from storage.models.storage import Storage
from state.models.treasury import Treasury
from bill.models.change_residency import ChangeResidency
from state.models.treasury_stock import TreasuryStock
from storage.models.good import Good
from django.db.models import F


@shared_task(name="residency_pay")
def residency_pay(treasury_pk):

    r = redis.StrictRedis(host='redis', port=6379, db=0)
    if r.exists(f'residency_pay_{treasury_pk}'):

        r.delete(f'residency_pay_{treasury_pk}')

    treasury = Treasury.get_instance(pk=treasury_pk)
    rifle = Good.objects.get(name_ru='Автоматы')
    drone = Good.objects.get(name_ru='Дроны')

    # если в казне нет одного из ресурсов - сразу чистим
    if TreasuryStock.objects.filter(treasury=treasury, good=rifle, stock=0).exists() \
            or TreasuryStock.objects.filter(treasury=treasury, good=drone, stock=0).exists():

        treasury.state.residency = 'free'
        treasury.state.save()

        PeriodicTask.objects.filter(pk=treasury.residency_id).delete()
        treasury.residency_id = None

        treasury.save()

        return

    regions_cnt = Region.objects.filter(state=treasury.state).count()

    rifle_cost = ChangeResidency.rifle_price * regions_cnt
    drone_cost = ChangeResidency.drone_price * regions_cnt

    if TreasuryStock.objects.filter(treasury=treasury, good=rifle, stock__gte=rifle_cost).exists() \
            and TreasuryStock.objects.filter(treasury=treasury, good=drone, stock__gte=drone_cost).exists():

        TreasuryStock.objects.filter(treasury=treasury,
                                     good=rifle,
                                     stock__gte=rifle_cost).update(stock=F('stock') - rifle_cost)

        TreasuryStock.objects.filter(treasury=treasury,
                                     good=drone,
                                     stock__gte=drone_cost).update(stock=F('stock') - drone_cost)

    else:

        treasury.state.residency = 'free'
        treasury.state.save()

        PeriodicTask.objects.filter(pk=treasury.residency_id).delete()
        treasury.residency_id = None

        treasury.save()