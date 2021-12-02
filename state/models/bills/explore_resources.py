# coding=utf-8

from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy
from decimal import Decimal
from region.region import Region
from state.models.bills.bill import Bill
from state.models.treasury import Treasury


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

        try:
            explore_region = int(request.POST.get('explore_regions'))

        except ValueError:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'ID региона должен быть целым числом',
            }

        if Region.objects.filter(pk=explore_region).exists():

            region = Region.objects.get(pk=explore_region)

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
        treasury = Treasury.objects.get(state=self.parliament.state)



        if treasury.cash != 0:

            region = Region.objects.get(pk=self.region.pk)

            cash_cost = float(
                getattr(region, self.resource + '_cap') - getattr(region, self.resource + '_has')) * self.exp_price

            from player.logs.print_log import log
            log(treasury.cash)
            log(cash_cost)

            if cash_cost <= treasury.cash:
                # обновляем запасы в регионе до максимума
                setattr(region, self.resource + '_has', getattr(region, self.resource + '_cap'))

                self.cash_cost = cash_cost
                setattr(treasury, 'cash', getattr(treasury, 'cash') - self.cash_cost)
                b_type = 'ac'

            else:
                # узнаем, сколько можем разведать максимум
                max_exp = treasury.cash / self.exp_price
                # если эта величина - как минимум один пункт
                if max_exp >= 0.01:
                    # обновляем запасы в регионе
                    setattr(region, self.resource + '_has', getattr(region, self.resource + '_has') + Decimal(max_exp))

                    self.cash_cost = treasury.cash
                    setattr(treasury, 'cash', treasury.cash % self.exp_price)
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

    def get_bill(self, player):

        # votes_pro = self.votes_pro.all()
        # votes_con = self.votes_con.all()

        data = {
            'bill': self,
            'title': self._meta.verbose_name_raw,
            'player': player,
            # 'votes_pro': votes_pro,
            # 'votes_con': votes_con,
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
