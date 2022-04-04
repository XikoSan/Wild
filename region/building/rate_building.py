# coding=utf-8
from django.db import models

from region.building.building import Building


# Абстрактный класс здания в регионе, имеющего рейтинговый индекс
# Позволяет создавать здания разных типов при общей механике подсчета рейтинга
class RateBuilding(Building):
    # Рейтинг здания
    top = models.IntegerField(default=1, verbose_name='Рейтинг здания')
    # словарь индексов, с процентом от числа зданий (за вычетом вышест. рейтингов)
    rating_percents = {}

    # словарь индексов конкретного здания, с соотв. эффектом
    indexes = {}

    # пересчитать рейтинг конкретных зданий
    @staticmethod
    def recount_rating():
        return

    # Указание абстрактности класса
    class Meta:
        abstract = True
