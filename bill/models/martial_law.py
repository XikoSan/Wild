# coding=utf-8
import datetime
from decimal import Decimal
from django.db import models
from django.db.models import F
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy
from math import ceil
from django.utils.translation import pgettext

from bill.models.bill import Bill
from region.models.region import Region
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.treasury import Treasury
from state.models.treasury_stock import TreasuryStock
from storage.models.good import Good
from war.models.martial import Martial
from django.utils.translation import pgettext_lazy

# Военное положение
class MartialLaw(Bill):
    # регион объявления
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион объявления')

    # режим
    modeChoices = (
        ('free', pgettext_lazy('martial_law_draft', 'Снятие ограничений')),
        ('set', pgettext_lazy('martial_law_draft', 'Военное положение')),
    )

    mode = models.CharField(
        max_length=4,
        choices=modeChoices,
        default='free',
    )

    @staticmethod
    def new_bill(request, player, parliament):

        if MartialLaw.objects.filter(running=True, initiator=player).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Ограничение: не более одного законопроекта данного типа'),
            }

        law_mode = request.POST.get('martial_law_mode')

        choice_list = []

        for choice in MartialLaw.modeChoices:
            choice_list.append(choice[0])

        if law_mode == '':
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Режим военного положения должен быть указан'),
            }

        elif not law_mode in choice_list:
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Такого режима военного положения не существует'),
            }

        try:
            martial_region = int(request.POST.get('martial_law_regions'))

        except ValueError:
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'ID региона должен быть целым числом'),
            }

        if Region.objects.filter(pk=martial_region, state=parliament.state).exists():

            region = Region.objects.get(pk=martial_region, state=parliament.state)

            if law_mode == 'free' and not Martial.objects.filter(active=True, region=region).exists():
                return {
                    'header': pgettext('new_bill', 'Новый законопроект'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                    'response': pgettext('new_bill', 'Этот режим военного положения уже выбран'),
                }

            if law_mode == 'set' and Martial.objects.filter(active=True, region=region).exists():

                return {
                    'header': pgettext('new_bill', 'Новый законопроект'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                    'response': pgettext('new_bill', 'Этот режим военного положения уже выбран'),
                }

            # если пытаются установить ВП, а с момента отмены предыдущего прошло менее двух недель
            if law_mode == 'set' and Martial.objects.filter(region=region,
                                                             active_end__gt=timezone.now() - datetime.timedelta(minutes=20160)
                                                            ).exists():
                return {
                    'header': pgettext('new_bill', 'Новый законопроект'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                    'response': pgettext('new_bill', 'Прошло менее двух недель с момента отмены предыдущего военного положения'),
                }

            # ура, все проверили
            bill = MartialLaw(
                running=True,
                parliament=parliament,
                initiator=player,
                voting_start=timezone.now(),

                region=region,
                mode=law_mode,
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
        treasury = Treasury.get_instance(state=self.parliament.state)

        # если пытаются установить ВП, а с момента отмены предыдущего прошло менее двух недель
        if self.mode == 'set' and Martial.objects.filter(region=self.region,
                                                         active_end__gt=timezone.now() - datetime.timedelta(
                                                                 minutes=20160)).exists():
            b_type = 'rj'

        else:
            # если ставят военку
            if self.mode == 'set':

                ifv = Good.objects.get(name_ru='БМП')

                # если в казне нет одного из ресурсов - сразу чистим
                if not TreasuryStock.objects.filter(treasury=treasury, good=ifv, stock__gte=24).exists():
                    b_type = 'rj'

                else:
                    TreasuryStock.objects.filter(treasury=treasury,
                                                 good=ifv,
                                                 stock__gte=24).update(stock=F('stock') - 24)

                    martial = Martial(
                        active=True,
                        region=self.region,
                        state=self.parliament.state,
                        days_left=1,
                    )
                    martial.save()
                    b_type = 'ac'

            # если снимают
            if self.mode == 'free':

                if Martial.objects.filter(active=True, region=self.region, state=self.parliament.state).exists():
                    martial = Martial.objects.get(
                        active=True,
                        region=self.region,
                        state=self.parliament.state
                    )
                    martial.disable_martial()

                b_type = 'ac'

        MartialLaw.objects.filter(pk=self.pk).update(type=b_type, running=False, voting_end=timezone.now())

    @staticmethod
    def get_draft(state):
        pass

    @staticmethod
    def get_new_draft(state):

        data = {
            'regions': Region.objects.filter(state=state),
        }

        return data, 'state/redesign/drafts/martial_law.html'

    def get_bill(self, player, minister, president):

        pass

    def get_new_bill(self, player, minister, president):

        has_right = False
        if minister:
            for right in minister.rights.all():
                if self.__class__.__name__ == right.right:
                    has_right = True
                    break

        data = {
            'bill': self,
            'title': self._meta.verbose_name,
            'player': player,
            'president': president,
            'has_right': has_right,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/redesign/bills/martial_law.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name, 'player': player}

        return data, 'state/gov/reviewed/martial_law.html'

    def get_new_reviewed_bill(self, player):
        data = {'bill': self, 'title': self._meta.verbose_name, 'player': player}

        return data, 'state/redesign/reviewed/martial_law.html'

    def __str__(self):
        return "Военное положение в " + self.region.region_name

    # Свойства класса
    class Meta:

        verbose_name = pgettext_lazy('new_bill', "Военное положение")
        verbose_name_plural = pgettext_lazy('new_bill', "Военные положения")


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=MartialLaw)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=MartialLaw)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()
