# coding=utf-8
import datetime
from decimal import Decimal
from django.apps import apps
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import pgettext
from django.utils.translation import pgettext_lazy
from math import ceil, floor

from bill.models.bill import Bill
from bill.models.explore_resources import ExploreResources
from player.views.multiple_sum import multiple_sum
from region.models.region import Region
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.treasury import Treasury
from war.models.martial import Martial


# Разведать ресурсы во всех регионах разом
class ExploreAll(Bill):
    # ресурс для разведки
    gold = 'gold'
    oil = 'oil'
    ore = 'ore'
    resExpChoices = (
        (gold, pgettext_lazy('explore_resources_draft', 'Золото')),
        (oil, pgettext_lazy('explore_resources_draft', 'Нефть')),
        (ore, pgettext_lazy('explore_resources_draft', 'Руда')),
    )
    resource = models.CharField(
        max_length=4,
        choices=resExpChoices,
        blank=True,
        null=True,
        default=None,
        verbose_name='Ресурс',
    )
    # объем разведки
    exp_value = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Общий объем разведки')
    # стоимость разведки за один пункт
    exp_price = multiple_sum(1000)

    @staticmethod
    def new_bill(request, player, parliament):

        if ExploreAll.objects.filter(running=True, initiator=player).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Ограничение: не более одного законопроекта данного типа'),
            }

        resources_list = []
        for resource in ExploreAll.resExpChoices:
            resources_list.append(resource[0])

        explore_resource = request.POST.get('explore_all_resources')

        if explore_resource in resources_list:

            # ура, все проверили
            bill = ExploreAll(
                running=True,
                parliament=parliament,
                initiator=player,
                voting_start=timezone.now(),

                resource=explore_resource,
            )
            bill.save()

            return {
                'response': 'ok',
            }

        else:
            return {
                'response': pgettext('new_bill', 'Нет такого ресурса'),
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }

    # выполнить законопроект
    def do_bill(self):
        b_type = None
        treasury = Treasury.get_instance(state=self.parliament.state)

        if treasury.cash != 0:

            #  получаем список регионов страны, в которых введено военное положение
            martials__pk = Martial.objects.filter(active=True, state=self.parliament.state).values_list('region__pk',
                                                                                                        flat=True).distinct()

            state_regions = Region.objects.filter(state=self.parliament.state).exclude(pk__in=martials__pk)

            cash_cost = 0
            ExploreAllRegion = apps.get_model("bill", "ExploreAllRegion")

            # считаем сколько стоит разведать на всю котлету
            for state_region in state_regions:
                prev_bills = ExploreResources.objects.filter(
                    parliament=self.parliament,
                    region=state_region,
                    resource=self.resource,
                    voting_end__gt=timezone.now() - datetime.timedelta(seconds=86400)
                ).values('region', 'resource').order_by('region').annotate(
                    exp_value=Coalesce(Sum('exp_value'), 0, output_field=models.DecimalField()))

                # Второй запрос - данные из ExploreAll и ExploreAllRegion
                explore_all_data = ExploreAllRegion.objects.filter(
                    exp_bill__parliament=self.parliament,
                    region=state_region,
                    exp_bill__resource=self.resource
                ).values('region', 'exp_bill__resource').order_by('region').annotate(
                    exp_value=Coalesce(Sum('exp_value'), 0, output_field=models.DecimalField())
                )

                # Объединение данных по региону и ресурсу
                combined_data = {}

                # Заполняем данные из prev_bills
                for bill in prev_bills:
                    key = (bill['region'], bill['resource'])
                    combined_data[key] = {
                        'region': bill['region'],
                        'resource': bill['resource'],
                        'exp_value': bill['exp_value']
                    }

                # Добавляем или обновляем данные из explore_all_data
                for explore in explore_all_data:
                    key = (explore['region'], explore['exp_bill__resource'])
                    if key in combined_data:
                        combined_data[key]['exp_value'] += explore['exp_value']
                    else:
                        combined_data[key] = {
                            'region': explore['region'],
                            'resource': explore['exp_bill__resource'],
                            'exp_value': explore['exp_value']
                        }

                # Результат в виде списка словарей
                result = list(combined_data.values())

                if result:
                    exp_mul = int(ceil(result[0]['exp_value'] / getattr(state_region, self.resource + '_cap')))
                    remainder = result[0]['exp_value'] % getattr(state_region, self.resource + '_cap')

                    if remainder == 0:
                        exp_mul += 1
                else:
                    exp_mul = 1

                cash_cost += float(
                    getattr(state_region, self.resource + '_cap') - getattr(state_region,
                                                                            self.resource + '_has')) * self.exp_price * exp_mul

            state_regions_u = []
            exp_all_regions_c = []
            if cash_cost <= treasury.cash:

                for state_region in state_regions:
                    volume = getattr(state_region, self.resource + '_cap') - getattr(state_region,
                                                                                     self.resource + '_has')
                    # обновляем запасы в регионе до максимума
                    setattr(state_region, self.resource + '_has', getattr(state_region, self.resource + '_cap'))
                    state_regions_u.append(state_region)

                    self.exp_value += Decimal(volume)

                    exp_all_regions_c.append(
                        ExploreAllRegion(
                            exp_bill=self,
                            region=state_region,
                            exp_value=Decimal(volume)
                        )
                    )

                self.cash_cost = cash_cost
                setattr(treasury, 'cash', getattr(treasury, 'cash') - self.cash_cost)
                b_type = 'ac'

            else:
                # нет денег разведать всё? На выход
                b_type = 'rj'

            # если закон принят
            if b_type == 'ac':
                self.save()
                treasury.save()

                if state_regions_u:
                    Region.objects.bulk_update(
                        state_regions_u,
                        fields=[self.resource + '_has', ],
                        batch_size=len(state_regions_u)
                    )

                if exp_all_regions_c:
                    ExploreAllRegion.objects.bulk_create(
                        exp_all_regions_c,
                        batch_size=len(exp_all_regions_c)
                    )

        else:
            b_type = 'rj'

        ExploreAll.objects.filter(pk=self.pk).update(type=b_type, running=False, voting_end=timezone.now())

    @staticmethod
    def get_draft(state):
        pass

    @staticmethod
    def get_new_draft(state):

        resources_dict = {}
        for resource in ExploreAll.resExpChoices:
            resources_dict[resource[0]] = resource[1]

        exp_cost = {}

        parliament = Parliament.objects.get(state=state)

        #  получаем список регионов страны, в которых введено военное положение
        martials__pk = Martial.objects.filter(active=True, state=state).values_list('region__pk', flat=True).distinct()

        state_regions = Region.objects.filter(state=state).exclude(pk__in=martials__pk)

        for resource in ExploreAll.resExpChoices:
            # считаем сколько стоит разведать на всю котлету
            for state_region in state_regions:

                prev_bills = ExploreResources.objects.filter(
                    parliament=parliament,
                    region=state_region,
                    resource=resource[0],
                    voting_end__gt=timezone.now() - datetime.timedelta(seconds=86400)
                ).values('region', 'resource').order_by('region').annotate(
                    exp_value=Coalesce(Sum('exp_value'), 0, output_field=models.DecimalField()))

                # Второй запрос - данные из ExploreAll и ExploreAllRegion
                ExploreAllRegion = apps.get_model("bill", "ExploreAllRegion")

                explore_all_data = ExploreAllRegion.objects.filter(
                    exp_bill__parliament=parliament,
                    region=state_region,
                    exp_bill__resource=resource[0]
                ).values('region', 'exp_bill__resource').order_by('region').annotate(
                    exp_value=Coalesce(Sum('exp_value'), 0, output_field=models.DecimalField())
                )

                # Объединение данных по региону и ресурсу
                combined_data = {}

                # Заполняем данные из prev_bills
                for bill in prev_bills:
                    key = (bill['region'], bill['resource'])
                    combined_data[key] = {
                        'region': bill['region'],
                        'resource': bill['resource'],
                        'exp_value': bill['exp_value']
                    }

                # Добавляем или обновляем данные из explore_all_data
                for explore in explore_all_data:
                    key = (explore['region'], explore['exp_bill__resource'])
                    if key in combined_data:
                        combined_data[key]['exp_value'] += explore['exp_value']
                    else:
                        combined_data[key] = {
                            'region': explore['region'],
                            'resource': explore['exp_bill__resource'],
                            'exp_value': explore['exp_value']
                        }

                # Результат в виде списка словарей
                result = list(combined_data.values())

                if result:
                    exp_mul = int(ceil(result[0]['exp_value'] / getattr(state_region, resource[0] + '_cap')))
                    remainder = result[0]['exp_value'] % getattr(state_region, resource[0] + '_cap')

                    if remainder == 0:
                        exp_mul += 1
                else:
                    exp_mul = 1

                if not resource[0] in exp_cost:
                    exp_cost[resource[0]] = 0

                exp_cost[resource[0]] += int(floor(Decimal(
                    getattr(state_region, resource[0] + '_cap') - getattr(state_region,
                                                                          resource[
                                                                              0] + '_has')) * ExploreAll.exp_price * exp_mul))

        data = {
            'resources': resources_dict,
            'exp_cost': exp_cost
        }

        return data, 'state/redesign/drafts/explore_all.html'

    def get_bill(self, player, minister, president):
        pass

    def get_new_bill(self, player, minister, president):

        has_right = False
        if minister:
            for right in minister.rights.all():
                if self.__class__.__name__ == right.right:
                    has_right = True
                    break

        #  получаем список регионов страны, в которых введено военное положение
        martials__pk = Martial.objects.filter(active=True, state=self.parliament.state).values_list('region__pk',
                                                                                                    flat=True).distinct()

        state_regions = Region.objects.filter(state=self.parliament.state).exclude(pk__in=martials__pk)

        total_var = Decimal('0.0')
        total_sum = 0

        # считаем сколько стоит разведать на всю котлету
        for state_region in state_regions:

            prev_bills = ExploreResources.objects.filter(
                parliament=self.parliament,
                region=state_region,
                resource=self.resource,
                voting_end__gt=timezone.now() - datetime.timedelta(seconds=86400)
            ).values('region', 'resource').order_by('region').annotate(
                exp_value=Coalesce(Sum('exp_value'), 0, output_field=models.DecimalField()))

            # Второй запрос - данные из ExploreAll и ExploreAllRegion
            ExploreAllRegion = apps.get_model("bill", "ExploreAllRegion")

            explore_all_data = ExploreAllRegion.objects.filter(
                exp_bill__parliament=self.parliament,
                region=state_region,
                exp_bill__resource=self.resource
            ).values('region', 'exp_bill__resource').order_by('region').annotate(
                exp_value=Coalesce(Sum('exp_value'), 0, output_field=models.DecimalField())
            )

            # Объединение данных по региону и ресурсу
            combined_data = {}

            # Заполняем данные из prev_bills
            for bill in prev_bills:
                key = (bill['region'], bill['resource'])
                combined_data[key] = {
                    'region': bill['region'],
                    'resource': bill['resource'],
                    'exp_value': bill['exp_value']
                }

            # Добавляем или обновляем данные из explore_all_data
            for explore in explore_all_data:
                key = (explore['region'], explore['exp_bill__resource'])
                if key in combined_data:
                    combined_data[key]['exp_value'] += explore['exp_value']
                else:
                    combined_data[key] = {
                        'region': explore['region'],
                        'resource': explore['exp_bill__resource'],
                        'exp_value': explore['exp_value']
                    }

            # Результат в виде списка словарей
            result = list(combined_data.values())

            if result:
                exp_mul = int(ceil(result[0]['exp_value'] / getattr(state_region, self.resource + '_cap')))
                remainder = result[0]['exp_value'] % getattr(state_region, self.resource + '_cap')

                if remainder == 0:
                    exp_mul += 1
            else:
                exp_mul = 1

            total_var += getattr(state_region, self.resource + '_cap') - getattr(state_region, self.resource + '_has')

            total_sum += int(floor(float(getattr(state_region, self.resource + '_cap') - getattr(state_region,
                                                                                       self.resource + '_has')) * ExploreAll.exp_price * exp_mul))

        data = {
            'total_var': total_var,
            'total_sum': int(total_sum),

            'bill': self,
            'title': self._meta.verbose_name,
            'player': player,
            'president': president,
            'has_right': has_right,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/redesign/bills/explore_all.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):
        pass

    def get_new_reviewed_bill(self, player):
        data = {'bill': self, 'title': self._meta.verbose_name, 'player': player}

        return data, 'state/redesign/reviewed/explore_all.html'

    def __str__(self):
        return str(self.exp_value) + " " + self.get_resource_display()

    # Свойства класса
    class Meta:

        verbose_name = pgettext_lazy('new_bill', "Разведка всех регионов")
        verbose_name_plural = pgettext_lazy('new_bill', "Разведки всех регионов")


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=ExploreAll)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=ExploreAll)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()
