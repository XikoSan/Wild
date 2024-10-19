# coding=utf-8
from decimal import Decimal
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import pgettext_lazy
from django.utils.translation import pgettext
from math import ceil

from bill.models.bill import Bill
from region.models.region import Region
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.treasury import Treasury


# Геологические изыскания
# снимает истощение запасов в регионе
class GeologicalSurveys(Bill):
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
    exp_value = models.IntegerField(default=0, verbose_name='Объем разведки')
    # Наличные
    drilling_cost = models.BigIntegerField(default=0, verbose_name='Наличные')
    # стоимость разведки за один пункт
    exp_price = 10

    @staticmethod
    def new_bill(request, player, parliament):

        if GeologicalSurveys.objects.filter(running=True, initiator=player).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Ограничение: не более одного законопроекта данного типа'),
            }

        try:
            explore_region = int(request.POST.get('survey_regions'))

        except ValueError:
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'ID региона должен быть целым числом'),
            }

        if Region.objects.filter(pk=explore_region, state=parliament.state).exists():

            region = Region.objects.get(pk=explore_region, state=parliament.state)

            resources_list = []
            for resource in GeologicalSurveys.resExpChoices:
                resources_list.append(resource[0])

            explore_resource = request.POST.get('survey_resources')

            if explore_resource in resources_list:

                if getattr(region, explore_resource + '_depletion') <= 0:
                    return {
                        'header': pgettext('new_bill', 'Новый законопроект'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                        'response': pgettext('new_bill', 'Истощения в регионе нет'),
                    }

                # ура, все проверили
                bill = GeologicalSurveys(
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

        if treasury.drilling != 0:

            region = Region.objects.get(pk=self.region.pk)

            if region.state == self.parliament.state:

                drilling_cost = int(getattr(region, self.resource + '_depletion')) * self.exp_price

                if drilling_cost <= treasury.drilling:
                    volume = int(
                        getattr(region, self.resource + '_cap') + getattr(region, self.resource + '_depletion'))
                    # обновляем запасы в регионе до максимума
                    setattr(region, self.resource + '_cap', volume)
                    setattr(region, self.resource + '_depletion', 0)

                    self.drilling_cost = drilling_cost
                    self.exp_value = volume
                    setattr(treasury, 'drilling', getattr(treasury, 'drilling') - self.drilling_cost)
                    b_type = 'ac'

                else:
                    # узнаем, сколько можем разведать максимум
                    exp_points = treasury.drilling // self.exp_price

                    # если есть хотя бы 10 штук
                    if exp_points >= 1:
                        # обновляем запасы в регионе
                        setattr(region, self.resource + '_cap', getattr(region, self.resource + '_cap') + exp_points)
                        setattr(region, self.resource + '_depletion',
                                getattr(region, self.resource + '_depletion') - exp_points)

                        self.drilling_cost = exp_points * self.exp_price
                        self.exp_value = exp_points * self.exp_price
                        setattr(treasury, 'drilling', treasury.drilling - self.drilling_cost)
                        b_type = 'ac'

                    else:
                        b_type = 'rj'

                # если закон принят
                if b_type == 'ac':
                    self.save()
                    treasury.save()
                    region.save()

            else:
                b_type = 'rj'
        else:
            b_type = 'rj'

        GeologicalSurveys.objects.filter(pk=self.pk).update(type=b_type, running=False, voting_end=timezone.now())

    @staticmethod
    def get_draft(state):

        resources_dict = {}
        for resource in GeologicalSurveys.resExpChoices:
            resources_dict[resource[0]] = resource[1]

        data = {'regions': Region.objects.filter(state=state), 'resources': resources_dict}

        return data, 'state/gov/drafts/geological_surveys.html'

    def get_bill(self, player, minister, president):

        has_right = False
        if minister:
            for right in minister.rights.all():
                if self.__class__.__name__ == right.right:
                    has_right = True
                    break

        data = {
            'bill': self,
            'title': self._meta.verbose_name_raw,
            'player': player,
            'president': president,
            'has_right': has_right,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/gov/bills/geological_surveys.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name_raw, 'player': player}

        return data, 'state/gov/reviewed/geological_surveys.html'

    def get_new_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name_raw, 'player': player}

        return data, 'state/redesign/reviewed/geological_surveys.html'

    def __str__(self):
        return str(self.exp_value) + " " + self.get_resource_display() + " в " + self.region.region_name

    # Свойства класса
    class Meta:
        # этот тип ЗП выключен
        abstract = True

        verbose_name = pgettext_lazy('new_bill', "Геологические изыскания")
        verbose_name_plural = pgettext_lazy('new_bill', "Геологические изыскания")


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=GeologicalSurveys)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=GeologicalSurveys)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()
