# coding=utf-8
from decimal import Decimal

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy
from state.models.parliament.deputy_mandate import DeputyMandate
from region.region import Region
from bill.models.bill import Bill
from state.models.treasury import Treasury
from state.models.parliament.parliament import Parliament

# Разведать ресурсы
class ExploreResources(Bill):
    # регион разведки
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион разведки')
    # ресурс для разведки
    gold = 'gold'
    oil = 'oil'
    ore = 'ore'
    resExpChoices = (
        (gold, gettext_lazy('Золото')),
        (oil, gettext_lazy('Нефть')),
        (ore, gettext_lazy('Руда')),
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
    exp_price = 100

    @staticmethod
    def new_bill(request, player, parliament):

        if ExploreResources.objects.filter(running=True, initiator=player).exists():
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Ограничение: не более одного законопроекта данного типа',
            }

        try:
            explore_region = int(request.POST.get('explore_regions'))

        except ValueError:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'ID региона должен быть целым числом',
            }

        if Region.objects.filter(pk=explore_region, state=parliament.state).exists():

            region = Region.objects.get(pk=explore_region, state=parliament.state)

            resources_list = []
            for resource in ExploreResources.resExpChoices:
                resources_list.append(resource[0])

            explore_resource = request.POST.get('explore_resources')

            if explore_resource in resources_list:

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
                    'response': 'Нет такого ресурса',
                    'header': 'Новый законопроект',
                    'grey_btn': 'Закрыть',
                }
        else:
            return {
                'response': 'Нет такого региона',
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
            }

    # выполнить законопроект
    def do_bill(self):
        b_type = None
        treasury = Treasury.get_instance(state=self.parliament.state)

        if treasury.cash != 0:

            region = Region.objects.get(pk=self.region.pk)

            cash_cost = float(
                getattr(region, self.resource + '_cap') - getattr(region, self.resource + '_has')) * self.exp_price

            if cash_cost <= treasury.cash:
                volume = getattr(region, self.resource + '_cap') - getattr(region, self.resource + '_has')
                # обновляем запасы в регионе до максимума
                setattr(region, self.resource + '_has', getattr(region, self.resource + '_cap'))

                self.cash_cost = cash_cost
                self.exp_value = Decimal(volume)
                setattr(treasury, 'cash', getattr(treasury, 'cash') - self.cash_cost)
                b_type = 'ac'

            else:
                # узнаем, сколько можем разведать максимум
                hund_price = self.exp_price / 100
                hund_points = treasury.cash // hund_price

                price = hund_points * hund_price

                # если эта величина - как минимум один пункт
                if hund_points >= 1:
                    # обновляем запасы в регионе
                    setattr(region, self.resource + '_has', getattr(region, self.resource + '_has') + Decimal(hund_points/100))

                    self.cash_cost = treasury.cash
                    self.exp_value = Decimal(hund_points/100)
                    setattr(treasury, 'cash', treasury.cash - price)
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

        ExploreResources.objects.filter(pk=self.pk).update(type=b_type, running=False, voting_end=timezone.now())

    @staticmethod
    def get_draft(state):

        resources_dict = {}
        for resource in ExploreResources.resExpChoices:
            resources_dict[resource[0]] = resource[1]

        data = {'regions': Region.objects.filter(state=state), 'resources': resources_dict}

        return data, 'state/gov/drafts/explore_resources.html'

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
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(state=player.region.state)).exists(),
        }

        return data, 'state/gov/bills/explore_resources.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name_raw, 'player': player}

        return data, 'state/gov/reviewed/explore_resources.html'

    def __str__(self):
        return str(self.exp_value) + " " + self.get_resource_display() + " в " + self.region.region_name

    # Свойства класса
    class Meta:

        verbose_name = "Разведка ресурсов"
        verbose_name_plural = "Разведки ресурсов"


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