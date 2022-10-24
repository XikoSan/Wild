# coding=utf-8

from django.db import models

from player.actual_manager import ActualManager
from player.player import Player

# Рамки аватара
class AvaBorder(models.Model):
    objects = models.Manager()  # Менеджер по умолчанию
    actual = ActualManager()  # Менеджер активных записей.

    # Название рамки
    title = models.CharField(max_length=100, blank=False, verbose_name='Название')

    # Описание набора
    description = models.CharField(max_length=500, blank=True, null=True, verbose_name='Описание')

    image = models.ImageField(upload_to='img/ava_borders/', blank=True, null=True, verbose_name='Рамка')

    # картинка стикера
    shape = models.TextField(default='', verbose_name='Рамка')

    box_x = models.DecimalField(default=00.00, max_digits=9, decimal_places=2, verbose_name='первое значение бокса')
    box_y = models.DecimalField(default=00.00, max_digits=9, decimal_places=2, verbose_name='второе значение бокса')

    # Цена набора
    price = models.IntegerField(default=1000, verbose_name='Цена')

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    def __str__(self):
        return str(self.title)

    # Свойства класса
    class Meta:
        verbose_name = "Рамка аватара"
        verbose_name_plural = "Рамки аватара"
