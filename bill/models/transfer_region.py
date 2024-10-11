# coding=utf-8

import datetime
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django.utils.translation import pgettext
from bill.models.bill import Bill
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
from war.models.martial import Martial


# Передать регион указанному государству
class TransferRegion(Bill):
    # возможность принять закон досрочно
    accept_ahead = False

    # регион объявления
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион объявления')

    # принимающее государство
    state = models.ForeignKey(State, on_delete=models.CASCADE, verbose_name='Принимает', related_name="catcher")

    acceptation_percent = 75

    @staticmethod
    def new_bill(request, player, parliament):

        if not request.POST.get('transfer_region_regions'):
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Не указан подходящий регион'),
            }

        if not request.POST.get('transfer_region_states'):
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Не указано подходящее государство'),
            }

        if TransferRegion.objects.filter(running=True, initiator=player).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Ограничение: не более одного законопроекта данного типа'),
            }

        try:
            transfer_region = int(request.POST.get('transfer_region_regions'))

        except ValueError:
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'ID региона должен быть целым числом'),
            }

        try:
            transfer_state = int(request.POST.get('transfer_region_states'))

        except ValueError:
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'ID государства должен быть целым числом'),
            }

        if Region.objects.filter(pk=transfer_region, state=parliament.state).exists():

            region = Region.objects.get(pk=transfer_region)

            if Martial.objects.filter(active=True, state=parliament.state, region=region).exists():
                return {
                    'header': pgettext('new_bill', 'Новый законопроект'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                    'response': pgettext('new_bill', 'В данном регионе введено военное положение'),
                }

            # регионы, с которых атакуют
            war_types = get_subclasses(War)
            for type in war_types:
                # если есть активные войны этого типа
                if type.objects.filter(running=True, deleted=False, agr_region=region).exists():
                    return {
                        'response': pgettext('new_bill', 'Регион является плацдармом атаки'),
                        'header': pgettext('new_bill', 'Новый законопроект'),
                        'grey_btn': pgettext('core', 'Закрыть'),
                    }

            if not State.actual.filter(pk=transfer_state).exists():
                return {
                    'response': pgettext('new_bill', 'Нет такого государства'),
                    'header': pgettext('new_bill', 'Новый законопроект'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }

            state = State.actual.get(pk=transfer_state)

            # ура, все проверили
            bill = TransferRegion(
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
                'response': pgettext('new_bill', 'Нет такого региона'),
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }

    # выполнить законопроект
    def do_bill(self):

        if Martial.objects.filter(active=True, state=self.parliament.state, region=self.region).exists():
            b_type = 'rj'

        else:
            b_type = 'ac'

        TransferRegion.objects.filter(pk=self.pk).update(type=b_type, running=False, voting_end=timezone.now())

    @staticmethod
    def get_draft(state):

        data = {
        }

        return data, 'state/gov/drafts/transfer_region.html'

    @staticmethod
    def get_new_draft(state):

        martial_regions = Martial.objects.filter(active=True, state=state).values_list('region__pk')
        mar_pk_list = []

        for m_reg in martial_regions:
            mar_pk_list.append(m_reg[0])

        regions = Region.objects.filter(state=state).exclude(limit_id__gt=0).exclude(pk__in=mar_pk_list)

        states = State.actual.exclude(pk=state.pk)

        # регионы, с которых атакуют
        agr_regions = []
        war_types = get_subclasses(War)
        for type in war_types:
            # если есть активные войны этого типа
            if type.objects.filter(running=True, deleted=False, agr_region__in=regions).exists():
                agr_regions.append(
                    type.objects.filter(running=True, deleted=False, agr_region__in=regions).values_list(
                        'agr_region__pk')
                )
        # удаляем дубли
        agr_regions = list(dict.fromkeys(agr_regions))

        regions = regions.exclude(pk__in=agr_regions)

        data = {
            'regions': regions,
            'states': states,
        }

        return data, 'state/redesign/drafts/transfer_region.html'

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

        return data, 'state/redesign/bills/transfer_region.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):

        data = {}

        return data, 'state/gov/reviewed/transfer_region.html'

    def get_new_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name_raw, 'player': player}

        return data, 'state/redesign/reviewed/transfer_region.html'

    def __str__(self):
        return self.region.region_name + " от " + self.parliament.state.title

    # Свойства класса
    class Meta:

        verbose_name = "Передача региона"
        verbose_name_plural = "Передачи регионов"


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=TransferRegion)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=TransferRegion)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()
