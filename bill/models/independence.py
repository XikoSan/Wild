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
from region.models.region import Region
from state.models.capital import Capital
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.parliament.parliament_party import ParliamentParty
from state.models.treasury import Treasury
from war.models.martial import Martial
from war.models.wars.war import War
from django.utils.translation import pgettext_lazy


# Объявить независимость региона
class Independence(Bill):
    # возможность принять закон досрочно
    accept_ahead = False

    # регион объявления
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион объявления')

    @staticmethod
    def new_bill(request, player, parliament):

        if not request.POST.get('independence_regions'):
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Не указан подходящий регион'),
            }

        if Independence.objects.filter(running=True, initiator=player).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Ограничение: не более одного законопроекта данного типа'),
            }

        try:
            independence_regions = int(request.POST.get('independence_regions'))

        except ValueError:
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'ID региона должен быть целым числом'),
            }

        if Region.objects.filter(pk=independence_regions, state=parliament.state).exists():

            region = Region.objects.get(pk=independence_regions, state=parliament.state)

            if Martial.objects.filter(active=True, state=parliament.state, region=region).exists():
                return {
                    'header': pgettext('new_bill', 'Новый законопроект'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                    'response': 'В данном регионе введено военное положение',
                }

            # столица этого госа
            if Capital.objects.filter(region=region).exists():
                return {
                    'response': pgettext('new_bill', 'Регион является столицей'),
                    'header': pgettext('new_bill', 'Новый законопроект'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }

            # его казна
            if Treasury.objects.filter(region=region, deleted=False).exists():
                return {
                    'response': pgettext('new_bill', 'В регионе размещена казна государства'),
                    'header': pgettext('new_bill', 'Новый законопроект'),
                    'grey_btn': pgettext('core', 'Закрыть'),
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

            # ура, все проверили
            bill = Independence(
                running=True,
                parliament=parliament,
                initiator=player,
                voting_start=timezone.now(),

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
        b_type = None

        if self.region.state == self.parliament.state:
            # столица этого госа
            if Capital.objects.filter(region=self.region).exists():
                b_type = 'rj'

            # его казна
            elif Treasury.objects.filter(region=self.region, deleted=False).exists():
                b_type = 'rj'

            #  если введено военное положение
            elif Martial.objects.filter(active=True, state=self.parliament.state, region=self.region).exists():
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

                if not war_has:
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

        Independence.objects.filter(pk=self.pk).update(type=b_type, running=False, voting_end=timezone.now())

    @staticmethod
    def get_draft(state):

        regions = Region.objects.filter(state=state)

        # столица этого госа
        capital_region_pk = Capital.objects.only("region").get(state=state).region.pk
        # его казна
        treasury_region_pk = Treasury.objects.only("region").get(state=state, deleted=False).region.pk
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

        regions = regions.exclude(pk=capital_region_pk).exclude(pk=treasury_region_pk).exclude(pk__in=agr_regions)

        data = {
            'regions': regions,
        }

        return data, 'state/gov/drafts/independence.html'

    @staticmethod
    def get_new_draft(state):

        martial_regions = Martial.objects.filter(active=True, state=state).values_list('region__pk')
        mar_pk_list = []

        for m_reg in martial_regions:
            mar_pk_list.append(m_reg[0])

        regions = Region.objects.filter(state=state).exclude(pk__in=mar_pk_list)

        # столица этого госа
        capital_region_pk = Capital.objects.only("region").get(state=state).region.pk
        # его казна
        treasury_region_pk = Treasury.objects.only("region").get(state=state, deleted=False).region.pk
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

        regions = regions.exclude(pk=capital_region_pk).exclude(pk=treasury_region_pk).exclude(pk__in=agr_regions)

        data = {
            'regions': regions,
        }

        return data, 'state/redesign/drafts/independence.html'

    def get_bill(self, player, minister, president):

        data = {
            'bill': self,
            'title': self._meta.verbose_name,
            'player': player,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/gov/bills/independence.html'

    def get_new_bill(self, player, minister, president):

        data = {
            'bill': self,
            'title': self._meta.verbose_name,
            'player': player,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/redesign/bills/independence.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name, 'player': player}

        return data, 'state/gov/reviewed/independence.html'

    def get_new_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name, 'player': player}

        return data, 'state/redesign/reviewed/independence.html'

    def __str__(self):
        return self.region.region_name + " от " + self.parliament.state.title

    # Свойства класса
    class Meta:

        verbose_name = pgettext_lazy('new_bill', "Объявление независимости")
        verbose_name_plural = pgettext_lazy('new_bill', "Объявления независимости")


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=Independence)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=Independence)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()
