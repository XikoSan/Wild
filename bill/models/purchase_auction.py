# coding=utf-8

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from bill.models.bill import Bill
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.treasury import Treasury
from state.models.treasury_lock import TreasuryLock
from storage.models.auction.auction import BuyAuction
from storage.models.auction.auction_lot import AuctionLot
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

        if PurchaseAuction.objects.filter(running=True, initiator=player).exists():
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Ограничение: не более одного законопроекта данного типа',
            }

        # получаем объем закупки
        try:
            purchase_value = int(request.POST.get('purchase_value'))

        except ValueError:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Объём закупки должна быть целым числом',
            }

        if not 0 < purchase_value < 1000000000000:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Объём закупки имеет ограничение в интервале от 0 до 1 000 000 000 000',
            }

        # получаем стоимость закупки
        try:
            purchase_price = int(request.POST.get('purchase_price'))

        except ValueError:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Цена закупки должна быть целым числом',
            }

        if not 0 < purchase_price < 1000000000000:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Цена закупки имеет ограничение в интервале от 0 до 1 000 000 000 000',
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
        b_type = None
        treasury = Treasury.get_instance(state=self.parliament.state)

        lots_list = []

        # узнаем, хватает ли денег в Казне, на блокировку
        if self.cash_cost <= treasury.cash:
            # вешаем на эти денежки блокировку
            treasury.cash -= self.cash_cost
            lock = TreasuryLock(
                lock_treasury=treasury,
                lock_good='cash',
                lock_count=self.cash_cost
            )

            # создаем Аукцион
            auction = BuyAuction(
                treasury_lock=lock,
                good=self.good,
                create_date=timezone.now()
            )

            # создаем Лоты аукциона
            buy_value_now = self.buy_value

            for lot_count in range(self.lots_count):

                if not (self.lots_count - lot_count == 0):
                    curr_lot_count = buy_value_now // (self.lots_count - lot_count)
                else:
                    curr_lot_count = buy_value_now

                lot = AuctionLot(
                    auction=auction,
                    count=curr_lot_count,
                    start_price=self.cash_cost / self.buy_value
                )

                buy_value_now -= curr_lot_count

                lots_list.append(lot)

            b_type = 'ac'

        else:
            b_type = 'rj'

        # если закон принят
        if b_type == 'ac':
            self.save()
            treasury.save()
            lock.save()
            auction.save()

            for lot in lots_list:
                lot.save()

        PurchaseAuction.objects.filter(pk=self.pk).update(type=b_type, running=False, voting_end=timezone.now())

    @staticmethod
    def get_draft(state):
        goods_dict = {}
        for resource in Storage.get_choises():
            goods_dict[resource[0]] = resource[1]

        data = {'goods_dict': goods_dict}

        return data, 'state/gov/drafts/purchase_auction.html'

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
