# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy

from player.logs.log import Log
from player.player import Player
from storage.models.storage import Storage


# запись об уничтожении ресурсов на Складах
class Destroy(Log):
    # склад списания ресурсов
    storage_from = models.ForeignKey(Storage, default=None, null=True, on_delete=models.CASCADE,
                                     verbose_name='Склад отправки', related_name='storage_source')

    # ------vvvvvvv------Минералы на складе------vvvvvvv------
    # Уголь
    coal = models.IntegerField(default=0, verbose_name=gettext_lazy('Уголь'))

    # Железо
    iron = models.IntegerField(default=0, verbose_name=gettext_lazy('iron'))

    # Бокситы
    bauxite = models.IntegerField(default=0, verbose_name=gettext_lazy('bauxite'))

    # ------vvvvvvv------Нефть на складе------vvvvvvv------
    # Нефть WTI
    wti_oil = models.IntegerField(default=0, verbose_name=gettext_lazy('wti_oil'))

    # Нефть Brent
    brent_oil = models.IntegerField(default=0, verbose_name=gettext_lazy('brent_oil'))

    # Нефть Urals
    urals_oil = models.IntegerField(default=0, verbose_name=gettext_lazy('urals_oil'))

    # ------vvvvvvv------Материалы на складе------vvvvvvv------
    # бензин
    gas = models.IntegerField(default=0, verbose_name=gettext_lazy('gas'))

    # бензин
    diesel = models.IntegerField(default=0, verbose_name=gettext_lazy('diesel'))

    steel = models.IntegerField(default=0, verbose_name=gettext_lazy('steel'))

    aluminium = models.IntegerField(default=0, verbose_name=gettext_lazy('alumunuim'))

    # ------vvvvvvv------Юниты на складе------vvvvvvv------
    # автоматы
    rifle = models.IntegerField(default=0, verbose_name=gettext_lazy('Автоматы'))
    # танки
    tank = models.IntegerField(default=0, verbose_name=gettext_lazy('tank'))
    # штурмовики
    jet = models.IntegerField(default=0, verbose_name=gettext_lazy('attack_air'))
    # орбитальные орудия
    station = models.IntegerField(default=0, verbose_name=gettext_lazy('orb_station'))
    # ПЗРК
    pzrk = models.IntegerField(default=0, verbose_name=gettext_lazy('mpads'))
    # AT-cannon
    antitank = models.IntegerField(default=0, verbose_name=gettext_lazy('antitank'))
    # гаубицы
    howitzer = models.IntegerField(default=0, verbose_name=gettext_lazy('howitzer'))

    def __str__(self):
        return self.storage_from.owner.nickname + " в " + self.storage_from.region.region_name + ": " + str(self.dtime.strftime('%Y-%m-%d %H:%M'))

    # Свойства класса
    class Meta:
        verbose_name = "Лог уничтожения ресурсов"
        verbose_name_plural = "Логи уничтожения"
