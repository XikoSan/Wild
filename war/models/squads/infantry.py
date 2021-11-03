# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy
from django.contrib.contenttypes.models import ContentType
from player.actual_manager import ActualManager
from war.models.squads.squad import Squad


# отряд пехоты армии игрока
class Infantry(Squad):
    objects = models.Manager()  # Менеджер по умолчанию
    actual = ActualManager()  # Менеджер активных записей

    specs = {
        'rifle':
            {
                'name': 'Автоматы',
                'energy': 1,
                'hp': 10,
                'damage':
                    {
                        'infantry': 6,
                        'lightvehicle': 1,
                    },
                'price': 52,
            },
    }

    # Автоматы
    rifle = models.IntegerField(default=0, verbose_name=gettext_lazy('Автоматы'))

    def __str__(self):
        return 'Отряд пехоты'

    # Свойства класса
    class Meta:
        verbose_name = "Отряд пехоты"
        verbose_name_plural = "Отряды пехоты"
