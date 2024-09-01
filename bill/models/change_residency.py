# coding=utf-8

import json
from django.apps import apps
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from bill.models.bill import Bill
from regime.presidential import Presidential
from regime.regime import Regime
from regime.temporary import Temporary
from region.models.region import Region
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.state import State
from state.models.treasury import Treasury
from state.models.treasury_stock import TreasuryStock
from storage.models.good import Good
from django.db.models import F


# Изменить способ получения прописки в государстве
# Не оптимизировать код хоткеями - ЗАТИРАЕТ ИМПОРТЫ !!
class ChangeResidency(Bill):
    # тип государства
    residencyTypeChoices = (
        ('free', 'Свободная'),
        ('issue', 'Выдаётся министром'),
    )

    residency = models.CharField(
        max_length=5,
        choices=residencyTypeChoices,
        default='free',
    )

    # стоимость
    rifle_cost = models.IntegerField(default=1, verbose_name='Стоимость - автоматы')
    drone_cost = models.IntegerField(default=1, verbose_name='Стоимость - дроны')

    rifle_price = 1
    drone_price = 1

    @staticmethod
    def new_bill(request, player, parliament):

        if ChangeResidency.objects.filter(running=True, initiator=player).exists():
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Ограничение: не более одного законопроекта данного типа',
            }

        new_form = request.POST.get('change_residency_residency')

        choice_list = []

        for choice in ChangeResidency.residencyTypeChoices:
            choice_list.append(choice[0])

        if new_form == '':
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Тип получения прописки должен быть указан',
            }

        elif not new_form in choice_list:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Такого типа получения прописки не существует',
            }

        if new_form == parliament.state.residency:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Этот тип получения прописки уже выбран',
            }

        # ура, все проверили
        bill = ChangeResidency(
            running=True,
            parliament=parliament,
            initiator=player,
            voting_start=timezone.now(),

            residency=new_form,
        )
        bill.save()

        return {
            'response': 'ok',
        }

    # выполнить законопроект
    def do_bill(self):
        b_type = None
        state = State.objects.get(pk=self.parliament.state.pk)

        rifle_cost = 0
        drone_cost = 0

        treasury = Treasury.get_instance(state=state)

        rifle = Good.objects.get(name_ru='Автоматы')
        drone = Good.objects.get(name_ru='Дроны')

        if self.residency == 'issue':

            regions_cnt = Region.objects.filter(state=treasury.state).count()

            rifle_cost = ChangeResidency.rifle_price * regions_cnt
            drone_cost = ChangeResidency.drone_price * regions_cnt

            if TreasuryStock.objects.filter(treasury=treasury, good=rifle, stock__gte=rifle_cost).exists()\
                    and TreasuryStock.objects.filter(treasury=treasury, good=drone, stock__gte=drone_cost).exists():

                state.residency = self.residency
                state.save()
                b_type = 'ac'

                schedule, created = CrontabSchedule.objects.get_or_create(
                    minute=f'{timezone.now().minute}',
                    hour='*',
                    day_of_week='*',
                    day_of_month='*',
                    month_of_year='*',
                )

                task = PeriodicTask(
                    name='прописка, id госа ' + str(state.pk),
                    task='residency_pay',
                    crontab=schedule,
                    args=json.dumps([treasury.id]),
                    start_time=timezone.now()
                )
                task.save()

                TreasuryStock.objects.filter(treasury=treasury,
                                             good=rifle,
                                             stock__gte=rifle_cost).update(stock=F('stock') - rifle_cost)

                TreasuryStock.objects.filter(treasury=treasury,
                                             good=drone,
                                             stock__gte=drone_cost).update(stock=F('stock') - drone_cost)

                treasury.residency_id = task.id
                treasury.save()

            else:
                b_type = 'rj'

        else:
            task_id = treasury.residency_id
            treasury.residency_id = None
            treasury.save()
            # удаляем таску
            PeriodicTask.objects.filter(pk=task_id).delete()

            state.residency = self.residency
            state.save()
            b_type = 'ac'

        ChangeResidency.objects.filter(pk=self.pk).update(
            type=b_type, running=False, voting_end=timezone.now(),
            rifle_cost=rifle_cost, drone_cost=drone_cost
        )

    @staticmethod
    def get_draft(state):

        regions_cnt = Region.objects.filter(state=state).count()

        data = {
            'rifle_cost': ChangeResidency.rifle_price * regions_cnt,
            'drone_cost': ChangeResidency.drone_price * regions_cnt,
        }

        return data, 'state/gov/drafts/change_residency.html'


    @staticmethod
    def get_new_draft(state):

        regions_cnt = Region.objects.filter(state=state).count()

        data = {
            'rifle_cost': ChangeResidency.rifle_price * regions_cnt,
            'drone_cost': ChangeResidency.drone_price * regions_cnt,
        }

        return data, 'state/redesign/drafts/change_residency.html'


    def get_bill(self, player, minister, president):

        has_right = False
        if minister:
            for right in minister.rights.all():
                if self.__class__.__name__ == right.right:
                    has_right = True
                    break

        regions_cnt = Region.objects.filter(state=player.region.state).count()

        data = {
            'bill': self,
            'title': self._meta.verbose_name_raw,
            'player': player,
            'president': president,
            'has_right': has_right,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),

            'rifle_cost': ChangeResidency.rifle_price * regions_cnt,
            'drone_cost': ChangeResidency.drone_price * regions_cnt,
        }

        return data, 'state/gov/bills/change_residency.html'

    def get_new_bill(self, player, minister, president):

        has_right = False
        if minister:
            for right in minister.rights.all():
                if self.__class__.__name__ == right.right:
                    has_right = True
                    break

        regions_cnt = Region.objects.filter(state=player.region.state).count()

        data = {
            'bill': self,
            'title': self._meta.verbose_name_raw,
            'player': player,
            'president': president,
            'has_right': has_right,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),

            'rifle_cost': ChangeResidency.rifle_price * regions_cnt,
            'drone_cost': ChangeResidency.drone_price * regions_cnt,
        }

        return data, 'state/redesign/bills/change_residency.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):

        regions_cnt = Region.objects.filter(state=player.region.state).count()

        data = {'bill': self, 'title': self._meta.verbose_name_raw, 'player': player,}

        return data, 'state/gov/reviewed/change_residency.html'

# получить шаблон рассмотренного законопроекта
    def get_new_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name_raw, 'player': player,}

        return data, 'state/redesign/reviewed/change_residency.html'

    # Свойства класса
    class Meta:
        # abstract = True
        verbose_name = "Новый способ выдачи прописки"
        verbose_name_plural = "Новые способы выдачи прописки"


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=ChangeResidency)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=ChangeResidency)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()
