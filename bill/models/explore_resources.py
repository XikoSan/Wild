# coding=utf-8
import datetime
from decimal import Decimal
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import pgettext
from django.utils.translation import pgettext_lazy
from math import ceil
from django.apps import apps
from bill.models.bill import Bill
from player.views.multiple_sum import multiple_sum
from region.models.region import Region
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.treasury import Treasury
from war.models.martial import Martial


# Разведать ресурсы
class ExploreResources(Bill):
    # регион разведки
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион разведки')
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
    exp_value = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Объем разведки')
    # стоимость разведки за один пункт
    exp_price = multiple_sum(1000)

    @staticmethod
    def new_bill(request, player, parliament):

        if ExploreResources.objects.filter(running=True, initiator=player).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Ограничение: не более одного законопроекта данного типа'),
            }

        try:
            explore_region = int(request.POST.get('explore_regions'))

        except ValueError:
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'ID региона должен быть целым числом'),
            }

        if Region.objects.filter(pk=explore_region, state=parliament.state).exists():

            region = Region.objects.get(pk=explore_region, state=parliament.state)

            if Martial.objects.filter(active=True, state=parliament.state, region=region).exists():
                return {
                    'header': pgettext('new_bill', 'Новый законопроект'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                    'response': pgettext('new_bill', 'В данном регионе введено военное положение'),
                }

            resources_list = []
            for resource in ExploreResources.resExpChoices:
                resources_list.append(resource[0])

            explore_resource = request.POST.get('explore_resources')

            if explore_resource in resources_list:

                if not getattr(region, explore_resource + '_cap') > getattr(region, explore_resource + '_has'):
                    return {
                        'header': pgettext('new_bill', 'Новый законопроект'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                        'response': pgettext('new_bill', 'Недопустима разведка в минус'),
                    }

                # ура, все проверили
                bill = ExploreResources(
                    running=True,
                    parliament=parliament,
                    initiator=player,
                    voting_start=timezone.now(),

                    region=region,
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
        else:
            return {
                'response': pgettext('new_bill', 'Нет такого региона'),
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }

    # выполнить законопроект
    def do_bill(self):
        b_type = None
        treasury = Treasury.get_instance(state=self.parliament.state)

        if treasury.cash != 0:

            region = Region.objects.get(pk=self.region.pk)

            #  если введено военное положение
            if Martial.objects.filter(active=True, state=self.parliament.state, region=self.region).exists():
                b_type = 'rj'

            else:

                if self.region.state == self.parliament.state:

                    prev_bills = ExploreResources.objects.filter(
                        parliament=self.parliament,
                        region=self.region,
                        resource=self.resource,
                        voting_end__gt=timezone.now() - datetime.timedelta(seconds=86400)
                    ).values('region', 'resource').order_by('region').annotate(
                        exp_value=Coalesce(Sum('exp_value'), 0, output_field=models.DecimalField()))

                    if prev_bills:
                        exp_mul = int(ceil(prev_bills[0]['exp_value'] / getattr(self.region, self.resource + '_cap')))
                        remainder = prev_bills[0]['exp_value'] % getattr(self.region, self.resource + '_cap')

                        if remainder == 0:
                            exp_mul += 1
                    else:
                        exp_mul = 1

                    cash_cost = float(
                        getattr(region, self.resource + '_cap') - getattr(region,
                                                                          self.resource + '_has')) * self.exp_price * exp_mul

                    if cash_cost <= treasury.cash:
                        volume = getattr(region, self.resource + '_cap') - getattr(region, self.resource + '_has')
                        # обновляем запасы в регионе до максимума
                        setattr(region, self.resource + '_has', getattr(region, self.resource + '_cap'))

                        # # истощение: смотрим, сколько десятков пунктов разведывают
                        # depletion = int(ceil(volume / 10))
                        # # уменьшаем лимит в регионе
                        # setattr(region, self.resource + '_cap', getattr(region, self.resource + '_cap') - depletion)
                        # # увеличиваем истощение
                        # setattr(region, self.resource + '_depletion', getattr(region, self.resource + '_depletion') + depletion)

                        self.cash_cost = cash_cost
                        self.exp_value = Decimal(volume)
                        setattr(treasury, 'cash', getattr(treasury, 'cash') - self.cash_cost)
                        b_type = 'ac'

                    else:
                        # узнаем, сколько можем разведать максимум
                        hund_price = (self.exp_price * exp_mul) / 100
                        hund_points = treasury.cash // hund_price

                        price = hund_points * hund_price

                        # если эта величина - как минимум один пункт
                        if hund_points >= 1:
                            # # истощение: смотрим, сколько десятков пунктов разведывают
                            # depletion = int(ceil(hund_points / 1000))
                            # # уменьшаем лимит в регионе
                            # setattr(region, self.resource + '_cap', getattr(region, self.resource + '_cap') - depletion)
                            # # увеличиваем истощение
                            # setattr(region, self.resource + '_depletion', getattr(region, self.resource + '_depletion') + depletion)

                            # обновляем запасы в регионе
                            setattr(region, self.resource + '_has',
                                    getattr(region, self.resource + '_has') + Decimal(hund_points / 100))

                            self.cash_cost = treasury.cash
                            self.exp_value = Decimal(hund_points / 100)
                            setattr(treasury, 'cash', treasury.cash - price)
                            b_type = 'ac'

                        else:
                            b_type = 'rj'
                else:
                    b_type = 'rj'

            # если закон принят
            if b_type == 'ac':
                self.save()
                treasury.save()
                region.save()

        else:
            b_type = 'rj'

        ExploreResources.objects.filter(pk=self.pk).update(type=b_type, running=False, voting_end=timezone.now())

    @staticmethod
    def get_draft(state):

        resources_dict = {}
        for resource in ExploreResources.resExpChoices:
            resources_dict[resource[0]] = resource[1]

        data = {'regions': Region.objects.filter(state=state), 'resources': resources_dict}

        return data, 'state/gov/drafts/explore_resources.html'

    @staticmethod
    def get_new_draft(state):

        resources_dict = {}
        for resource in ExploreResources.resExpChoices:
            resources_dict[resource[0]] = resource[1]

        parliament = Parliament.objects.get(state=state)

        prev_bills = ExploreResources.objects.filter(
            parliament=parliament,
            voting_end__gt=timezone.now() - datetime.timedelta(seconds=86400)
        ).values('region', 'resource').order_by('region').annotate(
            exp_value=Coalesce(Sum('exp_value'), 0, output_field=models.DecimalField()))

        exploration_dict = {}

        for line in prev_bills:
            if line['region'] not in exploration_dict:
                exploration_dict[line['region']] = {}

            if line['resource'] not in exploration_dict[line['region']]:
                exploration_dict[line['region']][line['resource']] = float(line['exp_value'])
            else:
                exploration_dict[line['region']][line['resource']] += float(line['exp_value'])

        # Дополнение exploration_dict данными из ExploreAllRegion
        # Получение модели через apps.get_model
        ExploreAllRegion = apps.get_model("bill", "ExploreAllRegion")
        # Получаем данные для текущего парламента и дополняем словарь
        extra_bills = ExploreAllRegion.objects.filter(
            exp_bill__parliament=parliament,
            exp_bill__voting_end__gt=timezone.now() - datetime.timedelta(seconds=86400)
        ).values('region', 'exp_bill__resource').order_by('region').annotate(
            exp_value=Coalesce(Sum('exp_value'), 0, output_field=models.DecimalField())  # Суммируем значения exp_value
        )

        # Заполнение словаря exploration_dict из extra_bills
        for line in extra_bills:
            # Если региона еще нет в словаре, добавляем его
            if line['region'] not in exploration_dict:
                exploration_dict[line['region']] = {}

            # Если ресурса еще нет в данном регионе, добавляем его с текущим значением
            if line['exp_bill__resource'] not in exploration_dict[line['region']]:
                exploration_dict[line['region']][line['exp_bill__resource']] = float(line['exp_value'])
            else:
                # Если ресурс уже есть, добавляем к нему текущее значение
                exploration_dict[line['region']][line['exp_bill__resource']] += float(line['exp_value'])

        # регионы с военным положением
        martial_regions = Martial.objects.filter(active=True, state=state).values_list('region__pk')
        mar_pk_list = []

        for m_reg in martial_regions:
            mar_pk_list.append(m_reg[0])

        regions = Region.objects.filter(state=state).exclude(pk__in=mar_pk_list)

        data = {
            'regions': regions,
            'resources': resources_dict,
            'exploration_dict': exploration_dict
        }

        return data, 'state/redesign/drafts/explore_resources.html'

    def get_bill(self, player, minister, president):

        has_right = False
        if minister:
            for right in minister.rights.all():
                if self.__class__.__name__ == right.right:
                    has_right = True
                    break

        data = {
            'bill': self,
            'title': self._meta.verbose_name,
            'player': player,
            'president': president,
            'has_right': has_right,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/gov/bills/explore_resources.html'

    def get_new_bill(self, player, minister, president):

        has_right = False
        if minister:
            for right in minister.rights.all():
                if self.__class__.__name__ == right.right:
                    has_right = True
                    break

        # Выборка данных из ExploreResources
        prev_bills = ExploreResources.objects.filter(
            parliament=self.parliament,
            region=self.region,
            resource=self.resource,
            voting_end__gt=timezone.now() - datetime.timedelta(seconds=86400)  # За последние 24 часа
        ).values('region', 'resource').order_by('region').annotate(
            exp_value=Coalesce(Sum('exp_value'), 0, output_field=models.DecimalField())  # Суммируем exp_value
        )

        ExploreAllRegion = apps.get_model("bill", "ExploreAllRegion")

        # Выборка данных из ExploreAllRegion
        extra_bills = ExploreAllRegion.objects.filter(
            exp_bill__parliament=self.parliament,
            region=self.region,
            exp_bill__resource=self.resource,  # С учетом текущего ресурса
            exp_bill__voting_end__gt=timezone.now() - datetime.timedelta(seconds=86400)
        ).values('region', 'exp_bill__resource').order_by('region').annotate(
            exp_value=Coalesce(Sum('exp_value'), 0, output_field=models.DecimalField())  # Суммируем exp_value
        )

        # Объединение данных из обеих выборок
        total_exp_value = 0  # Общая сумма exp_value

        if prev_bills:
            total_exp_value += float(prev_bills[0]['exp_value'])

        if extra_bills:
            total_exp_value += float(extra_bills[0]['exp_value'])

        # Вычисление exp_mul и remainder с учетом объединенной суммы
        if total_exp_value > 0:
            exp_mul = int(ceil(total_exp_value / float(getattr(self.region, self.resource + '_cap'))))
            remainder = total_exp_value % float(getattr(self.region, self.resource + '_cap'))

            if remainder == 0:
                exp_mul += 1
        else:
            exp_mul = 1

        data = {
            'bill': self,
            'title': self._meta.verbose_name,
            'player': player,
            'exp_mul': exp_mul,
            'president': president,
            'has_right': has_right,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/redesign/bills/explore_resources.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name, 'player': player}

        return data, 'state/gov/reviewed/explore_resources.html'

    def get_new_reviewed_bill(self, player):
        data = {'bill': self, 'title': self._meta.verbose_name, 'player': player}

        return data, 'state/redesign/reviewed/explore_resources.html'

    def __str__(self):
        return str(self.exp_value) + " " + self.get_resource_display() + " в " + self.region.region_name

    # Свойства класса
    class Meta:

        verbose_name = pgettext_lazy('new_bill', "Разведка ресурсов")
        verbose_name_plural = pgettext_lazy('new_bill', "Разведки ресурсов")


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=ExploreResources)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=ExploreResources)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()
