# coding=utf-8

from django.db import models

from region.region import Region


# Абстрактный класс здания в регионе
# Позволяет создавать здания разных типов при общей механике размещения и уровня
# todo: Сюда же можно вынести стоимость строительства
class Building(models.Model):
    # регион строительства
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион строительства')

    # Уровень здания
    level = models.IntegerField(default=0, verbose_name='Уровень здания')

    # потребление электричества, уровень
    power_consumption = 0

    # получить строки с информацией об уровне и рейтинге здания
    @staticmethod
    def get_stat(region):
        return

    def __str__(self):
        return self.region.region_name

    # Указание абстрактности класса
    class Meta:
        abstract = True
