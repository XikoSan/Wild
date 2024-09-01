import datetime
from celery import shared_task
from django.apps import apps
from django.db.models import F
from django.utils import timezone

from state.models.treasury import Treasury
from state.models.treasury_stock import TreasuryStock
from storage.models.good import Good
from war.models.martial import Martial


# раунд войны
@shared_task(name="pay_martial")
def pay_martial(id):
    # если нет объекта - на выход
    if not Martial.objects.filter(pk=id, active=True).exists():
        return

    # объект
    martial = Martial.objects.get(pk=id)

    # проверяем, что государство в регионе и Военке совпадают
    if not martial.region.state == martial.state:
        # удаляем военку
        martial.disable_martial()
        return

    # если нет Казны - на выход
    treasury = Treasury.get_instance(state=martial.state, deleted=False)

    if not treasury:
        # удаляем военку
        martial.disable_martial()
        return

    ifv = Good.objects.get(name_ru='БМП')

    # считаем, сколько нужно оплатить БМП для счастья
    if martial.days_left >= 14:
        ifv_cost = 360
    else:
        ifv_cost = (martial.days_left + 1) * 24

    # если в казне нет одного из ресурсов - сразу чистим
    if not TreasuryStock.objects.filter(treasury=treasury, good=ifv, stock__gte=ifv_cost).exists():
        # удаляем военку
        martial.disable_martial()
        return

    else:
        TreasuryStock.objects.filter(treasury=treasury,
                                     good=ifv,
                                     stock__gte=ifv_cost).update(stock=F('stock') - ifv_cost)

        martial.days_left += 1
        martial.save()


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
