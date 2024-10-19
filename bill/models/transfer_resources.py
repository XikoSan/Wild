# coding=utf-8

import datetime
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy
from math import ceil

from bill.models.bill import Bill
from gov.models.president import President
from gov.models.presidential_voting import PresidentialVoting
from gov.models.residency_request import ResidencyRequest
from party.party import Party
from player.views.get_subclasses import get_subclasses
from region.building.infrastructure import Infrastructure
from region.models.region import Region
from region.views.distance_counting import distance_counting
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.state import State
from django.utils.translation import pgettext
from state.models.treasury import Treasury
from state.models.treasury_lock import TreasuryLock
from state.models.treasury_stock import TreasuryStock
from storage.models.auction.auction import BuyAuction
from storage.models.good import Good
from storage.models.good_lock import GoodLock
from war.models.martial import Martial
from war.models.wars.war import War
from django.utils.translation import pgettext_lazy


# Передать ресурсы указанному государству
class TransferResources(Bill):
    # возможность принять закон досрочно
    accept_ahead = False

    # отправляемый товар
    send_good = models.ForeignKey(Good, blank=True, null=True, on_delete=models.CASCADE, verbose_name='Товар')

    # признак блокированных денег вместо товара
    send_cash = models.BooleanField(default=False, verbose_name='Отправка наличных')

    # количество отправляемого
    send_count = models.BigIntegerField(default=0, verbose_name='Количество')

    # казна, с которой списывают
    send_treasury = models.ForeignKey(Treasury, default=None, on_delete=models.CASCADE,
                                      verbose_name='Казна списания', related_name="send_treasury")

    # казна, в которую передают
    take_treasury = models.ForeignKey(Treasury, default=None, on_delete=models.CASCADE,
                                      verbose_name='Казна начисления', related_name="take_treasury")

    @staticmethod
    def new_bill(request, player, parliament):

        if not request.POST.get('transfer_state_to'):
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Не указано подходящее государство'),
            }

        if not request.POST.get('transfer_resources'):
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Не указан подходящий товар'),
            }

        if not request.POST.get('transfer_resources_value'):
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Не указано количество товара'),
            }

        # ------------

        if TransferResources.objects.filter(running=True, initiator=player).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Ограничение: не более одного законопроекта данного типа'),
            }

        # ------------

        try:
            transfer_value = int(request.POST.get('transfer_resources_value'))

        except ValueError:
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Количество товара должно быть целым числом'),
            }

        # ------------

        if not Treasury.objects.filter(state=parliament.state, deleted=False).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Не найдена казна государства'),
            }

        tres = Treasury.objects.get(state=parliament.state, deleted=False)

        # ------------

        try:
            transfer_res_pk = int(request.POST.get('transfer_resources'))

        except ValueError:
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'ID товара должен быть целым числом'),
            }

        if not Good.objects.filter(pk=transfer_res_pk).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Не найден товар с переданным ID'),
            }

        good = Good.objects.get(pk=transfer_res_pk)

        if not TreasuryStock.objects.filter(treasury=tres, good=good, stock__gte=transfer_value).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'В казне нет требуемого количества товара'),
            }

        # ------------

        try:
            transfer_state_pk = int(request.POST.get('transfer_state_to'))

        except ValueError:
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'ID региона должен быть целым числом'),
            }

        if not State.objects.filter(pk=transfer_state_pk, deleted=False).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Указанное государство не найдено'),
            }

        dest_state = State.objects.get(pk=transfer_state_pk, deleted=False)

        dest_tres = Treasury.objects.get(deleted=False, state=dest_state)

        # ------------

        # регионы, с которых атакуют
        war_types = get_subclasses(War)
        for type in war_types:
            if type.__name__ == 'EventWar':
                continue
            # если есть активные войны этого типа
            if type.objects.filter(running=True, deleted=False, def_region=tres.region).exists():
                return {
                    'response': pgettext('new_bill', 'Запрещено вывозить товары из атакованных регионов'),
                    'header': pgettext('new_bill', 'Новый законопроект'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }

        # ура, все проверили
        bill = TransferResources(
            running=True,
            parliament=parliament,
            initiator=player,
            voting_start=timezone.now(),

            send_good=good,
            send_count=transfer_value,
            send_treasury=tres,
            take_treasury=dest_tres,
        )
        bill.save()

        return {
            'response': 'ok',
        }

    # выполнить законопроект
    def do_bill(self):

        b_type = 'ac'

        # если на момент исполнения закона государство - получаетель не существует
        if self.take_treasury.state.deleted:
            b_type = 'rj'

        # если ресурсы в казне исчезли
        if not TreasuryStock.objects.filter(treasury=self.send_treasury, good=self.send_good, stock__gte=self.send_count).exists():
            b_type = 'rj'

        # регионы, с которых атакуют
        war_types = get_subclasses(War)
        for type in war_types:
            if type.__name__ == 'EventWar':
                continue
            # если есть активные войны этого типа
            if type.objects.filter(running=True, deleted=False, def_region=self.send_treasury.region).exists():
                b_type = 'rj'

        # цену доставки считаем
        trans_mul = ceil(distance_counting(self.send_treasury.region, self.take_treasury.region) / 100)

        send_infr_mul = Infrastructure.indexes[Infrastructure.get_stat(self.send_treasury.region)[0]['top']]
        dest_infr_mul = Infrastructure.indexes[Infrastructure.get_stat(self.take_treasury.region)[0]['top']]

        transfer_price = ceil( ceil(self.send_count * self.send_good.volume) * trans_mul * ( ( 100 - send_infr_mul - dest_infr_mul ) / 100 ) )

        if transfer_price > self.send_treasury.cash:
            b_type = 'rj'

        # проводка
        if b_type == 'ac':
            self.send_treasury.cash -= transfer_price
            self.send_treasury.save()

            # запас отправителя
            stock = TreasuryStock.objects.get(treasury=self.send_treasury, good=self.send_good, stock__gte=self.send_count)
            stock.stock -= self.send_count
            stock.save()

            # запас отправителя
            if not TreasuryStock.objects.filter(treasury=self.take_treasury, good=self.send_good).exists():
                dest_stock = TreasuryStock(treasury=self.take_treasury, good=self.send_good)
            else:
                dest_stock = TreasuryStock.objects.get(treasury=self.take_treasury, good=self.send_good)

            dest_stock.stock += self.send_count
            dest_stock.save()

        TransferResources.objects.filter(pk=self.pk).update(type=b_type, cash_cost=transfer_price,
                                                            running=False, voting_end=timezone.now())

    @staticmethod
    def get_new_draft(state):

        tres = Treasury.objects.get(state=state, deleted=False)

        # словарь склад - словарь стоимости до других регионов со складами:
        # москва:
        # - архангельск = 15
        # - питер       = 8
        # - моск. обл.  = 1
        trans_mul = {}

        dest_tres = Treasury.objects.filter(deleted=False)

        tres_stocks = TreasuryStock.objects.filter(treasury=tres, stock__gt=0)

        goods = []
        stocks = {}
        volumes = {}

        # заполняем список товаров, которые есть в казне
        # и сколько его там есть
        for stock in tres_stocks:

            # добавляем уникальный товар в список
            if stock.good not in goods:
                goods.append(stock.good)

            # словарь объёмов
            if stock.good not in volumes.keys():
                volumes[stock.good.pk] = stock.good.volume

            # заполняем словарь запасов
            stocks[stock.good.pk] = stock.stock

        infr_mul = {}
        # узнаем расстояния до складов
        for d_res in dest_tres:
            if not d_res == tres:
                trans_mul[d_res.pk] = ceil(distance_counting(tres.region, d_res.region) / 100)
            # узнаем множитель Инфраструктуры для этого региона
            infr_mul[d_res.pk] = Infrastructure.indexes[Infrastructure.get_stat(d_res.region)[0]['top']]

        states = State.actual.exclude(pk=state.pk)

        data = {
            'cash': tres.cash,
            'states': states,

            'goods': goods,
            'volumes': volumes,
            'stocks': stocks,

            'trans_mul': trans_mul,
            'infr_mul': infr_mul,
            'tres_pk': tres.pk,
        }

        return data, 'state/redesign/drafts/transfer_resources.html'

    def get_new_bill(self, player, minister, president):

        trans_mul = ceil(distance_counting(self.send_treasury.region, self.take_treasury.region) / 100)

        send_infr_mul = Infrastructure.indexes[Infrastructure.get_stat(self.send_treasury.region)[0]['top']]
        dest_infr_mul = Infrastructure.indexes[Infrastructure.get_stat(self.take_treasury.region)[0]['top']]

        transfer_price = ceil( ceil(self.send_count * self.send_good.volume) * trans_mul * ( ( 100 - send_infr_mul - dest_infr_mul ) / 100 ) )

        data = {
            'bill': self,
            'title': self._meta.verbose_name_raw,
            'player': player,
            'transfer_price': transfer_price,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/redesign/bills/transfer_resources.html'

    def get_new_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name_raw, 'player': player}

        return data, 'state/redesign/reviewed/transfer_resources.html'

    def __str__(self):
        return f'{ self.send_count } { self.send_good.name } в { self.take_treasury.state }'

    # Свойства класса
    class Meta:

        verbose_name = pgettext_lazy('new_bill', "Передача товаров")
        verbose_name_plural = pgettext_lazy('new_bill', "Передачи товаров")


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=TransferResources)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=TransferResources)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()
