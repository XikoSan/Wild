# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy
from django.contrib.contenttypes.models import ContentType
from player.actual_manager import ActualManager
from war.models.squads.squad import Squad


# отряд разведки армии игрока
class Recon(Squad):
    objects = models.Manager()  # Менеджер по умолчанию
    actual = ActualManager()  # Менеджер активных записей

    specs = {
        'drone':
            {
                'name': 'БПЛА',
                'energy': 1,
                'hp': 10,
                'damage':
                    {
                        'infantry': 0,
                        'lightvehicle': 0,
                        'heavyvehicle': 0,
                        'recon': 6,
                    },
                'price': 20,
            },
    }

    # БПЛА
    drone = models.IntegerField(default=0, verbose_name=gettext_lazy('БПЛА'))

    def __str__(self):
        return 'Отряд разведки'

    # Свойства класса
    class Meta:
        verbose_name = "Отряд разведки"
        verbose_name_plural = "Отряды разведки"
