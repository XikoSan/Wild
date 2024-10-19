# coding=utf-8
import datetime
import time
from django.db import models
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.utils.translation import pgettext
from django.utils.translation import pgettext_lazy

from player.views.get_subclasses import get_subclasses
from region.building.building import Building
from region.models.region import Region
from state.models.treasury import Treasury


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

    def plundering(self, count):

        if count < 100:
            return {
                       'response': 'Недостаточно энергии, необходимо: 100',
                       'header': 'Разграбление',
                   }, None

        if 1 > self.level:
            return {
                       'response': 'Недостаточно уровней Укреплений',
                       'header': 'Разграбление',
                   }, None

        self.level -= 1

        self.save()

        return None, 1

    # Свойства класса
    class Meta:
        verbose_name = pgettext_lazy('new_bill', "Укрепления")
        verbose_name_plural = pgettext_lazy('new_bill', "Укрепления")
