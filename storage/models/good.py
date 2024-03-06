# coding=utf-8
import datetime
from django.db import models
from django.utils.translation import gettext_lazy
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext as _

from modeltranslation.translator import translator, TranslationOptions

class GoodTranslation(TranslationOptions):
    fields = ('name',)


# Товар
class Good(models.Model):

    # название товара
    name = models.CharField(max_length=30, blank=False, verbose_name='Название')

    # занимаемое единицей число кубов
    volume = models.FloatField(default=1, verbose_name='Объём, шт.')

    # категория товара
    typeChoices = (
        ('minerals', pgettext_lazy('goods', 'Минералы')),
        ('oils', pgettext_lazy('goods', 'Нефть')),
        ('materials', pgettext_lazy('goods', 'Материалы')),
        ('equipments', pgettext_lazy('goods', 'Оборудование')),
        ('units', pgettext_lazy('goods', 'Оружие')),
    )
    type = models.CharField(
        max_length=10,
        choices=typeChoices,
        default='minerals',
    )

    # типоразмер
    sizeChoices = (
        ('large', pgettext_lazy('goods', 'Большой')),
        ('medium', pgettext_lazy('goods', 'Средний')),
        ('small', pgettext_lazy('goods', 'Малый')),
    )
    size = models.CharField(
        max_length=6,
        choices=sizeChoices,
        default='large',
    )

    def __str__(self):
        return self.name

    # Свойства класса
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

translator.register(Good, GoodTranslation)