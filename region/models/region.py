# coding=utf-8
import math

from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy, pgettext_lazy, ugettext as _

from state.models.state import State
from region.actual_manager import ActualManager
from storage.models.good import Good

# Чтобы перевод региона появился в PO файлах, требуется дописать его в конце html файла 'map'!
class Region(models.Model):
    with_off = models.Manager()  # Менеджер по умолчанию
    objects = ActualManager()  # Менеджер активных записей

    # регион выключен - не доступен спавн и перелёты
    is_off = models.BooleanField(default=False, verbose_name='Выключен')

    # название региона
    region_name = models.CharField(max_length=50, default=None, blank=True, null=True, verbose_name='Название региона')

    # название региона
    on_map_id = models.CharField(max_length=50, default='', verbose_name='ID на карте')

    # признак того что регион северный
    is_north = models.BooleanField(default=True, verbose_name='Северной широты')
    # координата широты
    north = models.DecimalField(default=00.00, max_digits=5, decimal_places=2)

    # признак того что регион восточный
    is_east = models.BooleanField(default=True, verbose_name='Восточной долготы')
    # координата долготы
    east = models.DecimalField(default=00.00, max_digits=5, decimal_places=2)
    # ---------- Государство ----------
    state = models.ForeignKey(State, default=None, blank=True, null=True, on_delete=models.SET_NULL,
                              verbose_name='Государство', related_name="reg_state")
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

    # ---------- Здания ----------
    # Уровень здания Госпиталь
    # med_lvl = models.IntegerField(default=0, verbose_name='Уровень госпиталя')
    # Рейтинг здания Госпиталь
    # med_top = models.IntegerField(default=1, verbose_name='Рейтинг госпиталя')
    #
    # # Уровень здания Полицейский участок
    # dpt_lvl = models.IntegerField(default=0, verbose_name='Уровень полиции')

    # ---------- Ресурсы ----------
    # Золотце:
    # в наличии
    gold_has = models.DecimalField(default=00.00, validators=[MinValueValidator(0)], max_digits=5, decimal_places=2,
                                   verbose_name='Золото: в наличии')
    # разведано
    gold_cap = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Золото: максимум')

    # истощение
    gold_depletion = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Истощение')

    # предел разведки
    # gold_explore_cap = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Золото: предел разведки')

    # Нефть:
    # в наличии
    oil_has = models.DecimalField(default=00.00, validators=[MinValueValidator(0)], max_digits=5, decimal_places=2,
                                  verbose_name='Нефть: в наличии')
    # максимум запасов
    oil_cap = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Нефть: максимум')

    # истощение
    oil_depletion = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='истощение')

    # предел разведки
    # oil_explore_cap = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Нефть: предел разведки')

    # oil_types = {
    #     'wti_oil': 'Нефть WTI',
    #     'brent_oil': 'Нефть Brent',
    #     'urals_oil': 'Нефть Urals',
    # }

    oil_types = ['WTI', 'Brent', 'Urals']

    # obsolete: марка добываемой нефти в регионе
    oil_type_choices = (
        ('wti_oil', pgettext_lazy('goods', 'WTI')),
        ('brent_oil', pgettext_lazy('goods', 'Brent')),
        ('urals_oil', pgettext_lazy('goods', 'Urals')),
    )
    oil_type = models.CharField(
        max_length=10,
        choices=oil_type_choices,
        default='urals_oil',
    )
    # марка добываемой нефти в регионе
    oil_mark =  models.ForeignKey(Good, default=None, on_delete=models.SET_NULL, null=True,
                                     verbose_name='Нефть')

    # Руда:
    # в наличии
    ore_has = models.DecimalField(default=00.00, validators=[MinValueValidator(0)], max_digits=5, decimal_places=2,
                                  verbose_name='Руда: в наличии')
    # максимум запасов
    ore_cap = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Руда: максимум')

    # потрачено пунктов разведки за сегодня
    ore_depletion = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='истощение')

    # # предел разведки
    # ore_explore_cap = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Руда: предел разведки')

    # obsolete: процент добываемого в регионе угля
    coal_proc = models.IntegerField(default=25, verbose_name='Процент угля')
    # obsolete: процент добываемого в регионе железа
    iron_proc = models.IntegerField(default=25, verbose_name='Процент железа')
    # obsolete: процент добываемого в регионе бокситов
    bauxite_proc = models.IntegerField(default=25, verbose_name='Процент бокситов')

    # централизация на карте
    longitude = models.DecimalField(default=00.00, max_digits=10, decimal_places=7, verbose_name='Долгота - центр')
    latitude = models.DecimalField(default=00.00, max_digits=10, decimal_places=7, verbose_name='Широта - центр')

    # сохранение профиля с изменением размеров и названия картинки профиля
    def save(self):
        super(Region, self).save()

    def clean(self):
        if self.coal_proc + self.iron_proc + self.bauxite_proc != 100:
            raise forms.ValidationError('Сумма процентов добываемых минералов должна быть равна ста')

    def __str__(self):
        return self.region_name

    # Свойства класса
    class Meta:
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"
