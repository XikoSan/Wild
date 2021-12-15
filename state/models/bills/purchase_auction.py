# coding=utf-8

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from state.models.bills.bill import Bill
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from storage.models.storage import Storage


# Аукцион закупки
class PurchaseAuction(Bill):
    # закупаемый ресурс
    good = models.CharField(
        max_length=10,
        choices=Storage.get_choises(),
        verbose_name='Закупаемый товар',
    )

    # объем закупки
    buy_value = models.BigIntegerField(default=0, verbose_name='Объем закупки')

    # количество лотов, на которое будет поделена закупка
    lots_count = models.BigIntegerField(default=0, verbose_name='Число лотов')

    @staticmethod
    def new_bill(request, player, parliament):
        # получаем объем закупки
        try:
            purchase_value = int(request.POST.get('purchase_value'))

        except ValueError:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Объём закупки должна быть целым числом',
            }

        if not 0 < purchase_value < 9223372036854775807:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Объём закупки должнен быть положительным INT',
            }

        # получаем стоимость закупки
        try:
            purchase_price = int(request.POST.get('purchase_price'))

        except ValueError:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Стоимость закупки должна быть целым числом',
            }

        if not 0 < purchase_price < 9223372036854775807:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Стоимость закупки должна быть положительным INT',
            }

        # получаем количество лотов
        try:
            purchase_lots = int(request.POST.get('purchase_lots'))

        except ValueError:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Количество лотов должно быть целым числом',
            }

        if not 0 < purchase_lots <= 10:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Количество лотов должно быть числом от 1 до 10',
            }

        if purchase_lots > purchase_value:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Количество лотов не может быть больше объёма закупки',
            }

        resources_list = []
        for resource in Storage.get_choises():
            resources_list.append(resource[0])

        explore_resource = request.POST.get('purchase_goods')

        if explore_resource in resources_list:

            # ура, все проверили
            bill = PurchaseAuction(
                running=True,
                parliament=parliament,
                initiator=player,
                voting_start=timezone.now(),

                good=explore_resource,
                buy_value=purchase_value,
                cash_cost=purchase_price * purchase_value,
                lots_count=purchase_lots,
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

    # выполнить законопроект
    def do_bill(self):
        pass
        # b_type = None
        # treasury = Treasury.objects.get(state=self.parliament.state)
        #
        # if treasury.cash != 0:
        #
        #     region = Region.objects.get(pk=self.region.pk)
        #
        #     cash_cost = float(
        #         getattr(region, self.resource + '_cap') - getattr(region, self.resource + '_has')) * self.exp_price
        #
        #     if cash_cost <= treasury.cash:
        #         volume = getattr(region, self.resource + '_cap') - getattr(region, self.resource + '_has')
        #         # обновляем запасы в регионе до максимума
        #         setattr(region, self.resource + '_has', getattr(region, self.resource + '_cap'))
        #
        #         self.cash_cost = cash_cost
        #         self.exp_value = Decimal(volume)
        #         setattr(treasury, 'cash', getattr(treasury, 'cash') - self.cash_cost)
        #         b_type = 'ac'
        #
        #     else:
        #         # узнаем, сколько можем разведать максимум
        #         hund_price = self.exp_price / 100
        #         hund_points = treasury.cash // hund_price
        #
        #         price = hund_points * hund_price
        #
        #         # если эта величина - как минимум один пункт
        #         if hund_points >= 1:
        #             # обновляем запасы в регионе
        #             setattr(region, self.resource + '_has',
        #                     getattr(region, self.resource + '_has') + Decimal(hund_points / 100))
        #
        #             self.cash_cost = treasury.cash
        #             self.exp_value = Decimal(hund_points / 100)
        #             setattr(treasury, 'cash', treasury.cash - price)
        #             b_type = 'ac'
        #
        #         else:
        #             b_type = 'rj'
        #
        #     # если закон принят
        #     if b_type == 'ac':
        #         self.save()
        #         treasury.save()
        #         region.save()
        #
        # else:
        #     b_type = 'rj'
        #
        # ExploreResources.objects.filter(pk=self.pk).update(type=b_type, running=False, voting_end=timezone.now())

    @staticmethod
    def get_draft(state):
        goods_dict = {}
        for resource in Storage.get_choises():
            goods_dict[resource[0]] = resource[1]

        data = {'goods_dict': goods_dict}

        return data, 'state/gov/drafts/purchase_auction.html'

    def get_bill(self, player):

        data = {
            'bill': self,
            'title': self._meta.verbose_name_raw,
            'player': player,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/gov/bills/purchase_auction.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name_raw, 'player': player}

        return data, 'state/gov/reviewed/purchase_auction.html'

    def __str__(self):
        return self.get_good_display()

    # Свойства класса
    class Meta:
        verbose_name = "Закупка товаров"
        verbose_name_plural = "Закупки товаров"


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=PurchaseAuction)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()
