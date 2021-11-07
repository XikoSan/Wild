# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy

from player.actual_manager import ActualManager
from war.models.squads.squad import Squad


# отряд тяжелой бронетехники армии игрока
class HeavyVehicle(Squad):
    objects = models.Manager()  # Менеджер по умолчанию
    actual = ActualManager()  # Менеджер активных записей

    specs = {
        'tank':
            {
                'name': 'Танки',
                'energy': 3,
                'hp': 50,
                'damage':
                    {
                        'infantry': 25,
                        'lightvehicle': 25,
                        'heavyvehicle': 25,
                    },
                'price': 905,
            },
    }

    # Танки
    tank = models.IntegerField(default=0, verbose_name=gettext_lazy('Танки'))

    def __str__(self):
        return 'Отряд тяжелой бронетехники'

    # Свойства класса
    class Meta:
        verbose_name = "Отряд тяжелой бронетехники"
        verbose_name_plural = "Отряды тяжелой бронетехники"
