# coding=utf-8
import datetime
from django.db import models
from django.utils.translation import gettext_lazy
from django.utils.translation import ugettext as _

from modeltranslation.translator import translator, TranslationOptions

class GoodTranslation(TranslationOptions):
    fields = ('name',)


# Товар
class Good(models.Model):

    # название товара
    name = models.CharField(max_length=30, blank=False, verbose_name='Название')

    # типоразмер
    sizeChoices = (
        ('large', 'Большой'),
        ('medium', 'Средний'),
        ('small', 'Малый'),
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