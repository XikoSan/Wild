# coding=utf-8

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import pgettext_lazy
from django.utils.translation import pgettext

from bill.models.bill import Bill
from region.models.region import Region
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.state import State


# Построить здание
class ChangeTaxes(Bill):
    # где меняем
    destination_vari = (
        ('Region', pgettext_lazy('change_taxes_draft', 'Регион')),
        ('State', pgettext_lazy('change_taxes_draft', 'Государство')),
    )
    destination = models.CharField(
        max_length=6,
        choices=destination_vari,
        blank=True,
        null=True,
        default=None,
        verbose_name='Режим ЗП',
    )

    # регион разведки
    region = models.ForeignKey(Region, default=None, null=True, on_delete=models.CASCADE, verbose_name='Регион смены')

    # что меняем
    tax_mod_vari = (
        ('cash', pgettext_lazy('change_taxes_draft', 'Финансирование')),
        ('oil', pgettext_lazy('change_taxes_draft', 'Нефть')),
        ('ore', pgettext_lazy('change_taxes_draft', 'Руда')),
        ('trade', pgettext_lazy('change_taxes_draft', 'Торговля')),
    )
    tax_mod = models.CharField(
        max_length=6,
        choices=tax_mod_vari,
        blank=True,
        null=True,
        default=None,
        verbose_name='Меняемый налог',
    )

    old_tax = models.DecimalField(default=00.00, validators=[MinValueValidator(0), MaxValueValidator(100)],
                                  max_digits=5, decimal_places=2, verbose_name='Старый налог')

    new_tax = models.DecimalField(default=00.00, validators=[MinValueValidator(0), MaxValueValidator(90)],
                                  max_digits=5, decimal_places=2, verbose_name='Новый налог')

    @staticmethod
    def new_bill(request, player, parliament):

        if ChangeTaxes.objects.filter(running=True, initiator=player).exists():
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Ограничение: не более одного законопроекта данного типа'),
            }

        # узнаем режим смены налогов
        destination = request.POST.get('change_taxes_destination')

        region = None

        # если только один регион
        if destination == 'destination_region':
            destination = 'Region'
            # получаем регион
            try:
                bill_region_pk = int(request.POST.get('change_taxes_regions'))

            except ValueError:
                return {
                    'header': pgettext('new_bill', 'Новый законопроект'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                    'response': pgettext('new_bill', 'ID региона должен быть целым числом'),
                }

            if Region.objects.filter(pk=bill_region_pk, state=parliament.state).exists():
                region = Region.objects.get(pk=bill_region_pk, state=parliament.state)

            else:
                return {
                    'response': pgettext('new_bill', 'Нет такого региона'),
                    'header': pgettext('new_bill', 'Новый законопроект'),
                    'grey_btn': pgettext('core', 'Закрыть'),
                }

        elif destination == 'destination_state':
            destination = 'State'

        else:
            return {
                'response': pgettext('new_bill', 'Не указана цель смены налога'),
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }

        # узнаем, какой налог меняем
        tax_mod = request.POST.get('change_taxes_tax_mod')

        if tax_mod not in ['cash', 'oil', 'ore', 'trade']:
            return {
                'response': pgettext('new_bill', 'Не указан изменяемый налог'),
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
            }

        # узнаем величину налога
        try:
            new_tax = int(request.POST.get('change_taxes_value'))

        except ValueError:
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Новая величина налога должна быть целым числом'),
            }

        # проверяем попадание в интервал 0..100
        if new_tax < 0 or new_tax > 90:
            return {
                'header': pgettext('new_bill', 'Новый законопроект'),
                'grey_btn': pgettext('core', 'Закрыть'),
                'response': pgettext('new_bill', 'Новая величина налога должна быть целым числом в интервале 0..90'),
            }

        # ура, все проверили
        bill = ChangeTaxes(
            running=True,
            parliament=parliament,
            initiator=player,
            voting_start=timezone.now(),

            destination=destination,
            region=region,
            tax_mod=tax_mod,
            new_tax=new_tax,
        )
        bill.save()

        return {
            'response': 'ok',
        }

    # выполнить законопроект
    def do_bill(self):
        b_type = old_tax = None

        if self.destination == 'State':
            state = State.objects.get(pk=self.parliament.state.pk)

            old_tax = getattr(state, self.tax_mod + '_tax')

            setattr(state, self.tax_mod + '_tax', self.new_tax)

            for region in Region.objects.filter(state=state):
                setattr(region, self.tax_mod + '_tax', self.new_tax)
                region.save()

            state.save()
            b_type = 'ac'

        else:
            region = Region.objects.get(pk=self.region.pk)

            if region.state == self.parliament.state:

                old_tax = getattr(region, self.tax_mod + '_tax')

                setattr(region, self.tax_mod + '_tax', self.new_tax)
                region.save()
                b_type = 'ac'

            else:
                b_type = 'rj'

        ChangeTaxes.objects.filter(pk=self.pk).update(type=b_type, running=False, old_tax=old_tax,
                                                      voting_end=timezone.now())

    # отменить законопроект
    def bill_cancel(self):

        if self.destination == 'State':
            state = State.objects.get(pk=self.parliament.state.pk)
            old_tax = getattr(state, self.tax_mod + '_tax')
        else:
            region = Region.objects.get(pk=self.region.pk)
            old_tax = getattr(region, self.tax_mod + '_tax')

        self.old_tax = old_tax

    @staticmethod
    def get_draft(state):

        data = {
            'regions': Region.objects.filter(state=state),
            'state': state,
        }

        return data, 'state/gov/drafts/change_taxes.html'

    @staticmethod
    def get_new_draft(state):

        data = {
            'regions': Region.objects.filter(state=state),
            'state': state,
        }

        return data, 'state/redesign/drafts/change_taxes.html'

    def get_bill(self, player, minister, president):

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

        return data, 'state/gov/bills/change_taxes.html'

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

        return data, 'state/redesign/bills/change_taxes.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name, 'player': player}

        return data, 'state/gov/reviewed/change_taxes.html'

    # получить шаблон рассмотренного законопроекта
    def get_new_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name, 'player': player}

        return data, 'state/redesign/reviewed/change_taxes.html'

    def __str__(self):
        return str(self.new_tax) + " " + self.get_tax_mod_display()

    # Свойства класса
    class Meta:

        verbose_name = pgettext_lazy('new_bill', "Изменение налогов")
        verbose_name_plural = pgettext_lazy('new_bill', "Изменения налогов")


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=ChangeTaxes)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=ChangeTaxes)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()
