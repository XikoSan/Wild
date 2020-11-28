# coding=utf-8
# import sys
# from PIL import Image
# from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
# from six import with_metaclass
# from io import BytesIO
# from django.utils.translation import get_language
# import gamecore.all_models.gov.state as ste


class Region(models.Model):
    # ---------------Ресурсы региона---------------
    # resourses = {
    #     'gold': 'Золото',
    #
    #     'oil': 'Нефть',
    #
    #     'ore': 'Руда',
    # }

    # название региона
    region_name = models.CharField(max_length=50, default=None, blank=True, null=True, verbose_name='Название региона')
    # название региона
    # on_map_id = models.CharField(max_length=50, verbose_name='ID на карте')

    # # признак того что регион северный
    # is_north = models.BooleanField(default=True, verbose_name='Северной широты')
    # # координата широты
    # north = models.DecimalField(default=00.00, max_digits=4, decimal_places=2)
    #
    # # признак того что регион восточный
    # is_east = models.BooleanField(default=True, verbose_name='Восточной долготы')
    # # координата долготы
    # east = models.DecimalField(default=00.00, max_digits=4, decimal_places=2)
    # ---------- Государство ----------
    # state = models.ForeignKey(ste.State, default=None, blank=True, null=True, on_delete=models.SET_NULL,
    #                           verbose_name='Государство', related_name="reg_state")
    # # признак столицы
    # capital = models.OneToOneField(ste.State, default=None, blank=True, null=True, on_delete=models.SET_NULL,
    #                                verbose_name='Столица государства', related_name="cap_state")
    # ---------- Налоги ----------
    # # Золотце:
    # gold_tax = models.DecimalField(default=00.00, validators=[MinValueValidator(0), MaxValueValidator(100)],
    #                                max_digits=5, decimal_places=2, verbose_name='Золото: налог')
    # # Нефть:
    # oil_tax = models.DecimalField(default=00.00, validators=[MinValueValidator(0), MaxValueValidator(100)],
    #                               max_digits=5, decimal_places=2, verbose_name='Нефть: налог')
    # # Руда:
    # ore_tax = models.DecimalField(default=00.00, validators=[MinValueValidator(0), MaxValueValidator(100)],
    #                               max_digits=5, decimal_places=2, verbose_name='Руда: налог')

    # ---------- Здания ----------
    # # Уровень здания Госпиталь
    # med_lvl = models.IntegerField(default=0, verbose_name='Уровень госпиталя')
    # # Рейтинг здания Госпиталь
    # med_top = models.IntegerField(default=0, verbose_name='Рейтинг госпиталя')
    #
    # # Уровень здания Полицейский участок
    # dpt_lvl = models.IntegerField(default=0, verbose_name='Уровень полиции')

    # ---------- Ресурсы ----------
    # Золотце:
    # в наличии
    # gold_has = models.DecimalField(default=00.00, validators=[MinValueValidator(0)], max_digits=5, decimal_places=2,
    #                                verbose_name='Золото: в наличии')
    # разведано
    # gold_cap = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Золото: максимум')

    # потрачено пунктов разведки за сегодня
    # gold_explored = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Золото: разведано')

    # предел разведки
    # gold_explore_cap = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Золото: предел разведки')

    # Нефть:
    # в наличии
    # oil_has = models.DecimalField(default=00.00, validators=[MinValueValidator(0)], max_digits=5, decimal_places=2,
    #                               verbose_name='Нефть: в наличии')
    # разведано
    # oil_cap = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Нефть: максимум')

    # потрачено пунктов разведки за сегодня
    # oil_explored = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Нефть: разведано')

    # предел разведки
    # oil_explore_cap = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Нефть: предел разведки')

    # Руда:
    # в наличии
    # ore_has = models.DecimalField(default=00.00, validators=[MinValueValidator(0)], max_digits=5, decimal_places=2,
    #                               verbose_name='Руда: в наличии')
    # разведано
    # ore_cap = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Руда: максимум')

    # потрачено пунктов разведки за сегодня
    # ore_explored = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Руда: разведано')

    # предел разведки
    # ore_explore_cap = models.DecimalField(default=00.00, max_digits=5, decimal_places=2, verbose_name='Руда: предел разведки')

    # shape = models.TextField(default=None, verbose_name='Вид на карте SVG')
    # централизация на карте
    # svg_x = models.IntegerField(default=0, verbose_name='центр на карте - Х')
    # svg_y = models.IntegerField(default=0, verbose_name='центр на карте - Y')

    # сохранение профиля с изменением размеров и названия картинки профиля
    def save(self):
        super(Region, self).save()

    def __str__(self):
        return self.region_name

    # Свойства класса
    class Meta:
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"


# Связь между двумя регионами: порядок не имеет значения
class Neighbours(models.Model):
    region_1 = models.ForeignKey(Region, default=None, null=True, on_delete=models.CASCADE, blank=False,
                                 verbose_name='Регион 1', related_name="region_1")
    region_2 = models.ForeignKey(Region, default=None, null=True, on_delete=models.CASCADE, blank=False,
                                 verbose_name='Регион 2', related_name="region_2")

    def __str__(self):
        return self.region_1.region_name + ' < - > ' + self.region_2.region_name

    # Свойства класса
    class Meta:
        verbose_name = "Связь регионов"
        verbose_name_plural = "Связи регионов"
