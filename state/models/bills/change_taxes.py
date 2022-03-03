# coding=utf-8

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy

from region.region import Region
from state.models.bills.bill import Bill
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.state import State
from storage.models.storage import Storage


# Построить здание
class ChangeTaxes(Bill):
    # где меняем
    destination_vari = (
        ('Region', gettext_lazy('Регион')),
        ('State', gettext_lazy('Государство')),
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
        ('cash', gettext_lazy('Финансирование')),
        ('oil', gettext_lazy('Нефть')),
        ('ore', gettext_lazy('Руда')),
        ('trade', gettext_lazy('Торговля')),
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

    new_tax = models.DecimalField(default=00.00, validators=[MinValueValidator(0), MaxValueValidator(100)],
                                  max_digits=5, decimal_places=2, verbose_name='Новый налог')

    @staticmethod
    def new_bill(request, player, parliament):
        pass
        if ChangeTaxes.objects.filter(running=True, initiator=player).exists():
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Ограничение: не более одного законопроекта данного типа',
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
                    'header': 'Новый законопроект',
                    'grey_btn': 'Закрыть',
                    'response': 'ID региона должен быть целым числом',
                }

            if Region.objects.filter(pk=bill_region_pk).exists():
                region = Region.objects.get(pk=bill_region_pk)

            else:
                return {
                    'response': 'Нет такого региона',
                    'header': 'Новый законопроект',
                    'grey_btn': 'Закрыть',
                }

        elif destination == 'destination_state':
            destination = 'State'

        else:
            return {
                'response': 'Не указана цель смены налога',
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
            }

        # узнаем, какой налог меняем
        tax_mod = request.POST.get('change_taxes_tax_mod')

        if tax_mod not in ['cash', 'oil', 'ore', 'trade']:
            return {
                'response': 'Не указан изменяемый налог',
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
            }

        # узнаем величину налога
        try:
            new_tax = int(request.POST.get('change_taxes_value'))

        except ValueError:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Новая величина налога должна быть целым числом',
            }

        # проверяем попадание в интервал 0..100
        if new_tax < 0 or new_tax > 100:
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Новая величина налога должна быть целым числом в интервале 0..100',
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

        else:
            region = Region.objects.get(pk=self.region.pk)

            old_tax = getattr(region, self.tax_mod + '_tax')

            setattr(region, self.tax_mod + '_tax', self.new_tax)
            region.save()

        b_type = 'ac'

        ChangeTaxes.objects.filter(pk=self.pk).update(type=b_type, running=False, old_tax=old_tax, voting_end=timezone.now())

    @staticmethod
    def get_draft(state):

        data = {
            'regions': Region.objects.filter(state=state),
            'state': state,
        }

        return data, 'state/gov/drafts/change_taxes.html'

    def get_bill(self, player):

        data = {
            'bill': self,
            'title': self._meta.verbose_name_raw,
            'player': player,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/gov/bills/change_taxes.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):

        data = {'bill': self, 'title': self._meta.verbose_name_raw, 'player': player}

        return data, 'state/gov/reviewed/change_taxes.html'

    def __str__(self):
        return str(self.new_tax) + " " + self.get_tax_mod_display()

    # Свойства класса
    class Meta:
        verbose_name = "Изменение налогов"
        verbose_name_plural = "Изменения налогов"


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=ChangeTaxes)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()
