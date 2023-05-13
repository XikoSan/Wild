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

@shared_task(name="residency_pay")
def residency_pay(treasury_pk):

    treasury = Treasury.get_instance(pk=treasury_pk)

    regions_cnt = Region.objects.filter(state=treasury.state).count()

    if getattr(treasury, 'rifle') - (ChangeResidency.rifle_price*regions_cnt) < 0\
            or getattr(treasury, 'drone') - (ChangeResidency.drone_price*regions_cnt) < 0:

        treasury.state.residency = 'free'
        treasury.state.save()

        PeriodicTask.objects.filter(pk=treasury.residency_id).delete()
        treasury.residency_id = None

    else:
        setattr(treasury, 'rifle', getattr(treasury, 'rifle') - (ChangeResidency.rifle_price*regions_cnt))
        setattr(treasury, 'drone', getattr(treasury, 'drone') - (ChangeResidency.drone_price*regions_cnt))

    treasury.save()