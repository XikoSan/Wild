# coding=utf-8

import datetime
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy

from bill.models.bill import Bill
from bill.models.transfer_region import TransferRegion
from gov.models.president import President
from gov.models.presidential_voting import PresidentialVoting
from gov.models.residency_request import ResidencyRequest
from party.party import Party
from player.views.get_subclasses import get_subclasses
from region.building.building import Building
from region.building.hospital import Hospital
from region.models.region import Region
from state.models.capital import Capital
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.parliament.parliament_party import ParliamentParty
from state.models.state import State
from state.models.treasury import Treasury
from state.models.treasury_lock import TreasuryLock
from state.models.treasury_stock import TreasuryStock
from storage.models.auction.auction import BuyAuction
from storage.models.good import Good
from storage.models.good_lock import GoodLock
from war.models.wars.war import War


# Принять регион
class TransferAccept(Bill):
    # возможность принять закон досрочно
    accept_ahead = False

    # регион объявления
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион объявления')

    # отдающее государство
    state = models.OneToOneField(State, on_delete=models.CASCADE, verbose_name='Отдаёт', related_name="sender")

    acceptation_percent = 75

    @staticmethod
    def new_bill(request, player, parliament):

        if not request.POST.get('transfer_region_regions'):
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Не указан подходящий регион',
            }

        if not request.POST.get('transfer_region_states'):
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Не указан подходящий регион',
            }

        if TransferAccept.objects.filter(running=True, initiator=player).exists():
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Ограничение: не более одного законопроекта данного типа',
            }

        try:
            transfer_region = int(request.POST.get('transfer_region_regions'))

        except ValueError:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'ID региона должен быть целым числом',
            }

        try:
            transfer_state = int(request.POST.get('transfer_region_states'))

        except ValueError:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'ID региона должен быть целым числом',
            }

        if not State.actual.filter(pk=transfer_state).exists():
            return {
                'response': 'Нет такого государства',
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
            }

        state = State.actual.get(pk=transfer_state)

        if Region.objects.filter(pk=transfer_region, state=state).exists():

            sender_parl = Parliament.objects.get(state=state)
            region = Region.objects.get(pk=transfer_region)

            if TransferRegion.objects.filter(running=True,
                                             parliament=sender_parl,
                                             region=region,
                                             state=parliament.state,
                                             ).exists():
                return {
                    'header': 'Новый законопроект',
                    'grey_btn': 'Закрыть',
                    'response': 'Указанный регион не передаётся',
                }

            # ура, все проверили
            bill = TransferAccept(
                running=True,
                parliament=parliament,
                initiator=player,
                voting_start=timezone.now(),

                state=state,
                region=region,
            )
            bill.save()

            return {
                'response': 'ok',
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

        if self.region.state == self.state:

            sender_parl = Parliament.objects.get(state=self.state)

            if not TransferRegion.objects.filter(running=False,
                                                 parliament=sender_parl,
                                                 region=self.region,
                                                 state=self.parliament.state,
                                                 voting_end__gte=timezone.now() - datetime.timedelta(seconds=10800)
                                                 ).exists():
                b_type = 'rj'

            else:
                war_has = False
                # регионы, с которых атакуют
                war_types = get_subclasses(War)
                for type in war_types:
                    # если есть активные войны этого типа
                    if type.objects.filter(running=True, deleted=False, agr_region=self.region).exists():
                        war_has = True
                        b_type = 'rj'
                        break

                # если этот рег атакован
                if not war_has:
                    for type in war_types:
                        # если есть активные войны этого типа
                        if type.objects.filter(running=True, deleted=False, def_region=self.region).exists():
                            war_has = True
                            b_type = 'rj'
                            break

                if not war_has:

                    # если это столичный регион
                    if Capital.objects.filter(region=self.region).exists():
                        # если есть другой регион
                        if Region.objects.filter(state=self.state).exclude(pk=self.region.pk).exists():

                            # переместить столицу
                            top_hospital = Hospital.objects.filter(
                                region__in=Region.objects.filter(state=self.state).exclude(pk=self.region.pk)
                            ).order_by('-top').first()

                            # находим лучший регион по медицине, ставим столицу там
                            capital = Capital.objects.get(state=self.region.state, region=self.region)
                            capital.region = top_hospital.region
                            capital.save()

                            # переместить казну
                            if Treasury.objects.filter(region=self.region, deleted=False).exists():
                                tres = Treasury.objects.get(region=self.region, deleted=False)

                                tres.region = top_hospital.region
                                tres.save()

                            # принят
                            b_type = 'ac'

                        # иначе
                        else:
                            # передать казну
                            if Treasury.objects.filter(region=self.region, deleted=False).exists():

                                all_goods = Good.objects.all()

                                agr_tres = Treasury.objects.get(state=self.state)
                                tres = Treasury.objects.get(region=self.region, deleted=False)

                                # передаем деньги в полном объёме
                                agr_tres.cash += getattr(tres, 'cash')

                                for good in all_goods:
                                    # если у врага в казне есть такой товар
                                    if TreasuryStock.objects.filter(treasury=tres, good=good, stock__gt=0).exists():
                                        def_tres_stock = TreasuryStock.objects.get(treasury=tres, good=good)
                                        # если уже есть запас у агрессора
                                        if TreasuryStock.objects.filter(treasury=agr_tres, good=good).exists():
                                            agr_tres_stock = TreasuryStock.objects.get(treasury=agr_tres, good=good)
                                        else:
                                            agr_tres_stock = TreasuryStock(treasury=agr_tres, good=good)
                                        # отдаем все в принимающую казну
                                        agr_tres_stock.stock += def_tres_stock.stock
                                        agr_tres_stock.save()

                                # если есть блокировки - их тоже захватываем
                                if TreasuryLock.objects.filter(lock_treasury=tres, deleted=False).exists():
                                    for lock in TreasuryLock.objects.filter(lock_treasury=tres, deleted=False):
                                        if lock.cash:
                                            agr_tres.cash += lock.lock_count

                                        else:
                                            # если уже есть запас у агрессора
                                            if TreasuryStock.objects.filter(treasury=agr_tres,
                                                                            good=lock.lock_good).exists():
                                                agr_tres_stock = TreasuryStock.objects.get(treasury=agr_tres,
                                                                                           good=lock.lock_good)
                                            else:
                                                agr_tres_stock = TreasuryStock(treasury=agr_tres, good=lock.lock_good)
                                            # отдаем получающему регион
                                            agr_tres_stock.stock += lock.lock_count
                                            agr_tres_stock.save()

                                        # удаляем блокировку
                                        lock.deleted = True
                                        lock.save()

                                        # закупки ресурсов отменяем
                                        if BuyAuction.actual.filter(treasury_lock=lock).exists():
                                            auction = BuyAuction.actual.get(treasury_lock=lock)
                                            # и таску удаляет, и метку ставит
                                            auction.delete_task()

                                agr_tres.save()

                            # роспуск госуадсртва
                            self.region.state.dissolution()

                            # принят
                            b_type = 'ac'

                    else:
                        # получить партии этого рега
                        reg_parties = Party.objects.filter(region=self.region, deleted=False).values_list('pk')
                        # узнать депутатов перед удалением
                        deputates = DeputyMandate.objects.only("player").filter(party__pk__in=reg_parties).values_list(
                            'player')

                        # удаляем голоса этих депутатов из ЗП
                        bills_list = []
                        bills_classes = get_subclasses(Bill)

                        # для каждого типа законопроектов:
                        for type in bills_classes:
                            # если есть активные законы в этом парламенте
                            if type.objects.filter(parliament=self.parliament, running=True).exists():
                                for bill in type.objects.filter(parliament=self.parliament, running=True):
                                    for deputate in deputates:

                                        if deputate in bill.votes_pro.all():
                                            bill.votes_pro.remove()

                                        elif deputate in bill.votes_pro.all():
                                            bill.votes_con.remove()

                        # теперь можно чистить депутатов
                        DeputyMandate.objects.filter(party__pk__in=reg_parties).update(player=None)

                        # если есть президент (как должность)
                        if President.objects.filter(state=self.parliament.state).exists():
                            # през
                            pres = President.objects.get(state=self.parliament.state)
                            # если идут его выборы
                            if PresidentialVoting.objects.filter(running=True,
                                                                 president=pres
                                                                 ).exists():
                                # выборы
                                voting = PresidentialVoting.objects.get(running=True,
                                                                        president=pres
                                                                        )

                                for candidate in voting.candidates.all():
                                    # если партия кандидата из нашего региона - удаляем его
                                    if candidate.party and candidate.party.region == self.region:
                                        voting.candidates.remove(candidate)
                                voting.save()

                        # сбрасывать налоги на ноль
                        Region.objects.filter(pk=self.region.pk).update(
                            cash_tax=0,
                            oil_tax=0,
                            ore_tax=0,
                            trade_tax=0,
                            state=None,
                            peace_date=timezone.now() + datetime.timedelta(days=14)
                        )
                        # чистить запросы прописки в этот рег
                        ResidencyRequest.objects.filter(region=self.region).delete()
                        # принят
                        b_type = 'ac'

        else:
            b_type = 'rj'

        TransferAccept.objects.filter(pk=self.pk).update(type=b_type, running=False, voting_end=timezone.now())

    @staticmethod
    def get_draft(state):

        data = {
        }

        return data, 'state/gov/drafts/transfer_accept.html'

    @staticmethod
    def get_new_draft(state):
        # либо закончилось последние три часа, либо еще идет
        transfers = TransferRegion.objects.filter(state=state).filter(
            Q(running=True)
            | Q(running=False, voting_end__gte=timezone.now() - datetime.timedelta(seconds=10800))
        )

        data = {
            'transfers': transfers,
        }

        return data, 'state/redesign/drafts/transfer_accept.html'

    def get_bill(self, player, minister, president):

        data = {
        }

        return data, 'state/gov/bills/transfer_region.html'

    def get_new_bill(self, player, minister, president):

        data = {
            'bill': self,
            'title': self._meta.verbose_name_raw,
            'player': player,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/redesign/bills/transfer_accept.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):

        data = {}

        return data, 'state/gov/reviewed/transfer_accept.html'

    def get_new_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name_raw, 'player': player}

        return data, 'state/redesign/reviewed/transfer_accept.html'

    def __str__(self):
        return self.region.region_name + " от " + self.parliament.state.title

    # Свойства класса
    class Meta:

        verbose_name = "Принятие региона"
        verbose_name_plural = "Принятия регионов"


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=TransferAccept)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=TransferAccept)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()
