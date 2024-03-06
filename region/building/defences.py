# coding=utf-8
from django.db import models
from django.utils import timezone
from player.views.get_subclasses import get_subclasses
from region.building.building import Building
from region.models.region import Region
from state.models.treasury import Treasury
from django.db.models import F
import datetime
from django.db import transaction
import time
# Укрепления - здание в регионе
class Defences(Building):

    # потребление электричества, уровень
    power_consumption = 1

    # получить строки с информацией об уровне и рейтинге здания
    @staticmethod
    def get_stat(region):

        if Defences.objects.filter(region=region).exists():
            defences = Defences.objects.get(region=region)

            level = defences.level

        else:
            level = 0

        data = {
            'level': level,
        }

        return data, 'region/redesign/buildings/defences.html'

    # Свойства класса
    class Meta:
        verbose_name = "Укрепления"
        verbose_name_plural = "Укрепления"
