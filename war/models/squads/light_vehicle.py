# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy
from django.contrib.contenttypes.models import ContentType
from player.actual_manager import ActualManager
from war.models.squads.squad import Squad


# отряд легкой бронетехники армии игрока
class LightVehicle(Squad):
    objects = models.Manager()  # Менеджер по умолчанию
    actual = ActualManager()  # Менеджер активных записей

    specs = {
        'ifv':
            {
                'name': 'БМП',
                'energy': 2,
                'hp': 25,
                'damage':
                    {
                        'infantry': 16,
                        'lightvehicle': 10,
                    },
                'price': 450,
            },
    }

    # БМП
    ifv = models.IntegerField(default=0, verbose_name=gettext_lazy('БМП'))

    def __str__(self):
        return 'Отряд легкой бронетехники'

    # Свойства класса
    class Meta:
        verbose_name = "Отряд легкой бронетехники"
        verbose_name_plural = "Отряды легкой бронетехники"
