# coding=utf-8

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy

from bill.models.bill import Bill
from party.party import Party
from player.views.get_subclasses import get_subclasses
from region.building.building import Building
from region.region import Region
from state.models.capital import Capital
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.parliament.parliament_party import ParliamentParty
from state.models.treasury import Treasury
from war.models.wars.war import War
from gov.models.residency_request import ResidencyRequest

# Объявить независимость региона
class Independence(Bill):
    # возможность принять закон досрочно
    accept_ahead = False

    # регион объявления
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион объявления')

    @staticmethod
    def new_bill(request, player, parliament):

        if Independence.objects.filter(running=True, initiator=player).exists():
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Ограничение: не более одного законопроекта данного типа',
            }

        try:
            independence_regions = int(request.POST.get('independence_regions'))

        except ValueError:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'ID региона должен быть целым числом',
            }

        if Region.objects.filter(pk=independence_regions, state=parliament.state).exists():

            region = Region.objects.get(pk=independence_regions, state=parliament.state)

            # столица этого госа
            if Capital.objects.filter(region=region).exists():
                return {
                    'response': 'Регион является столицей',
                    'header': 'Новый законопроект',
                    'grey_btn': 'Закрыть',
                }

            # его казна
            if Treasury.objects.filter(region=region).exists():
                return {
                    'response': 'В регионе размещена казна государства',
                    'header': 'Новый законопроект',
                    'grey_btn': 'Закрыть',
                }

            # регионы, с которых атакуют
            war_types = get_subclasses(War)
            for type in war_types:
                # если есть активные войны этого типа
                if type.objects.filter(running=True, deleted=False, agr_region=region).exists():
                    return {
                        'response': 'Регион является плацдармом атаки',
                        'header': 'Новый законопроект',
                        'grey_btn': 'Закрыть',
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
                'response': 'Нет такого региона',
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
            }

    # выполнить законопроект
    def do_bill(self):
        b_type = None

        if self.region.state == self.parliament.state:
            # столица этого госа
            if Capital.objects.filter(region=self.region).exists():
                b_type = 'rj'

            # его казна
            elif Treasury.objects.filter(region=self.region).exists():
                b_type = 'rj'

            else:
                war_has = False
                # регионы, с которых атакуют
                war_types = get_subclasses(War)
                for type in war_types:
                    # если есть активные войны этого типа
                    if type.objects.filter(running=True, deleted=False, agr_region=self.region).exists():
                        war_has = True
                        break

                if not war_has:
                    # получить партии этого рега
                    reg_parties = Party.objects.filter(region=self.region, deleted=False).values_list('pk')
                    # узнать депутатов перед удалением
                    deputates = DeputyMandate.objects.only("player").filter(party__pk__in=reg_parties).values_list('player')

                    # удаляем голоса этих депутатов из ЗП
                    bills_list = []
                    bills_classes = get_subclasses(Bill)

                    # для каждого типа законопроектов:
                    for type in bills_classes:
                        # если есть активные законы в этом парламенте
                        if type.objects.filter(parliament=self.parliament, running=True).exists():
                            for bill in type.objects.filter(parliament=self.parliament, running=True):
                                for deputate in deputates:

                                    if deputate in bill.votes_pro:
                                        bill.votes_pro.remove()

                                    elif deputate in bill.votes_pro:
                                        bill.votes_con.remove()

                    # теперь можно чистить депутатов
                    DeputyMandate.objects.filter(party__pk__in=reg_parties).update(player=None)

                    # сбрасывать налоги на ноль
                    Region.objects.filter(pk=self.region.pk).update(
                        cash_tax = 0,
                        oil_tax = 0,
                        ore_tax = 0,
                        trade_tax = 0,
                        state = None
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

    def get_bill(self, player, minister, president):

        data = {
            'bill': self,
            'title': self._meta.verbose_name_raw,
            'player': player,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/gov/bills/independence.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name_raw, 'player': player}

        return data, 'state/gov/reviewed/independence.html'

    def __str__(self):
        return self.region.region_name + " от " + self.parliament.state.title

    # Свойства класса
    class Meta:

        verbose_name = "Объявление независимости"
        verbose_name_plural = "Объявления независимости"


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
