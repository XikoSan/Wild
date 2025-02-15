# coding=utf-8

from django.apps import apps
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from player.actual_manager import ActualManager
from regime.regime import Regime
from django.utils.translation import gettext_lazy, pgettext_lazy
from storage.models.good import Good


class State(models.Model):
    objects = models.Manager()  # Менеджер по умолчанию
    actual = ActualManager()  # Менеджер активных записей

    # название страны
    title = models.CharField(max_length=50, verbose_name='Название государства')
    # герб страны
    image = models.ImageField(upload_to='img/state_avatars/', blank=True, null=True, verbose_name='Герб')
    # цвет на карте
    color = models.CharField(max_length=6, default="008542", verbose_name='Цвет государства')
    # время основания партии
    foundation_date = models.DateTimeField(default=timezone.now, blank=True, null=True)

    # приветственное сообщение государства
    message = models.CharField(max_length=300, blank=True, default='', verbose_name='сообщение')

    # тип государства
    stateTypeChoices = (
        ('Temporary', pgettext_lazy('state_view', 'Временное правительство')),
        ('Presidential', pgettext_lazy('state_view', 'Президентская республика')),
    )
    type = models.CharField(
        max_length=15,
        choices=stateTypeChoices,
        default='Temporary',
    )
    # прописка
    residencyTypeChoices = (
        ('free', pgettext_lazy('state_view', 'Свободная')),
        ('issue', pgettext_lazy('state_view', 'Выдаётся министром')),
    )
    residency = models.CharField(
        max_length=5,
        choices=residencyTypeChoices,
        default='free',
    )
    # ---------- Налоги ----------
    # Деньги:
    cash_tax = models.DecimalField(default=00.00, validators=[MinValueValidator(0), MaxValueValidator(100)],
                                   max_digits=5, decimal_places=2, verbose_name='Деньги: налог')
    # Нефть:
    oil_tax = models.DecimalField(default=00.00, validators=[MinValueValidator(0), MaxValueValidator(100)],
                                  max_digits=5, decimal_places=2, verbose_name='Нефть: налог')
    # Руда:
    ore_tax = models.DecimalField(default=00.00, validators=[MinValueValidator(0), MaxValueValidator(100)],
                                  max_digits=5, decimal_places=2, verbose_name='Руда: налог')
    # Торговля:
    trade_tax = models.DecimalField(default=00.00, validators=[MinValueValidator(0), MaxValueValidator(100)],
                                   max_digits=5, decimal_places=2, verbose_name='Торговля: налог')

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    # id фонового процесса (начала или конца праймериз)
    # task_id = models.CharField(max_length=150, blank=True, null=True, verbose_name='id фонового процесса')

    # роспуск правительства данного государства, в зависимости от формы правления
    def dissolution(self):
        current_regime_cl = None
        # получаем текущий режим из свойств госа
        for regime_cl in Regime.__subclasses__():
            if self.type == regime_cl.__name__:
                current_regime_cl = regime_cl
                break

        if current_regime_cl:
            current_regime_cl.dissolution(self)

            Region = apps.get_model('region', 'Region')
            Region.objects.filter(state=self).update(state=None)

            self.deleted = True
            self.save()


    # получить налог с указанной суммы указанного ресурса
    @staticmethod
    def check_taxes(region, sum, mode):

        Martial = apps.get_model('war', 'Martial')
        taxed_sum = sum

        # если в регионе есть гос
        if region.state and not Martial.objects.filter(active=True, region=region, state=region.state).exists():
            # если налог в регион не равен налогу в государстве
            if getattr(region, mode + '_tax') != getattr(region.state, mode + '_tax'):
                # берем из региона
                tax_value = getattr(region, mode + '_tax')
            else:
                # неважно откуда брать налог
                tax_value = getattr(region, mode + '_tax')

            # получаем налог по ставке, которую получили
            tax = int(sum * (float(tax_value) / 100))
            # сумма "на руки"
            taxed_sum = sum - tax

        return taxed_sum

    # получить налог с указанной суммы указанного ресурса
    @staticmethod
    def get_taxes(region, sum, mode, resource):

        Martial = apps.get_model('war', 'Martial')
        taxed_sum = sum

        # если в регионе есть гос
        if region.state and not Martial.objects.filter(active=True, region=region, state=region.state).exists():
            # казна
            treasury_cl = apps.get_model('state.Treasury')
            treasury = treasury_cl.get_instance(state=region.state, deleted=False)

            # если налог в регион не равен налогу в государстве
            if getattr(region, mode + '_tax') != getattr(region.state, mode + '_tax'):
                # берем из региона
                tax_value = getattr(region, mode + '_tax')
            else:
                # неважно откуда брать налог
                tax_value = getattr(region, mode + '_tax')

            # получаем налог по ставке, которую получили
            tax = int(sum * (float(tax_value) / 100))
            # сумма "на руки"
            taxed_sum = sum - tax
            # начисляем налог в казну
            if resource == 'cash':
                setattr(treasury, resource, getattr(treasury, resource) + tax)
                treasury.save()

            else:
                TreasuryStock = apps.get_model('state.TreasuryStock')

                if TreasuryStock.objects.filter(good=resource, treasury=treasury).exists():
                    stock = TreasuryStock.objects.get(good=resource, treasury=treasury)

                else:
                    stock = TreasuryStock(
                                            good=resource,
                                            treasury=treasury
                                          )

                stock.stock += tax
                stock.save()

        return taxed_sum

    # # сохранение государства с изменением размеров и названия картинки профиля
    # def save(self):
    #     # если картинка есть (добавили или изменили)
    #     if self.image:
    #         # Opening the uploaded image
    #         im = Image.open(self.image)
    #
    #         output = BytesIO()
    #
    #         # Resize/modify the image
    #         im = im.resize((300, 300))
    #
    #         # after modifications, save it to the output
    #         im.save(output, format='PNG', quality=100)
    #         output.seek(0)
    #
    #         # change the imagefield value to be the newley modifed image value
    #         self.image = InMemoryUploadedFile(output, 'ImageField', "%(state)s.png" % {"state": self.title},
    #                                           'image/png',
    #                                           sys.getsizeof(output), None)
    #
    #         super(State, self).save()
    #     # если картинку удалили или её не было
    #     else:
    #         super(State, self).save()

    def __str__(self):
        return self.title

    # Свойства класса
    class Meta:
        verbose_name = "Государство"
        verbose_name_plural = "Государства"
