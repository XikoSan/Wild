# coding=utf-8
from django.apps import apps
from django.db import models

from storage.models.good import Good
from factory.models.blueprint import Blueprint


# Компонент для производства товара
class Component(models.Model):
    # чертёж
    blueprint = models.ForeignKey(Blueprint, on_delete=models.CASCADE, verbose_name='Чертёж')

    # сырьё для производства
    good = models.ForeignKey(Good, on_delete=models.CASCADE, verbose_name='Сырьё')

    # требуемое количество
    count = models.IntegerField(default=0, verbose_name='Количество')

    def __str__(self):
        return f'{self.blueprint.good.name}: {self.blueprint} {self.good.name}'

    # Свойства класса
    class Meta:
        verbose_name = "Компонент"
        verbose_name_plural = "Компоненты"
