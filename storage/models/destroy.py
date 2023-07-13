# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy, pgettext_lazy

from player.logs.log import Log
from player.player import Player
from storage.models.storage import Storage
from storage.models.good import Good


# запись об уничтожении ресурсов на Складах
class Destroy(Log):
    # склад списания ресурсов
    storage_from = models.ForeignKey(Storage, default=None, null=True, on_delete=models.CASCADE,
                                     verbose_name='Склад отправки', related_name='storage_source')

    # товар
    good = models.ForeignKey(Good, default=None, null=True, on_delete=models.CASCADE, verbose_name='Товар')

    # количество
    count = models.IntegerField(default=0, verbose_name='Количество')

    # ------vvvvvvv------Минералы на складе------vvvvvvv------
    # Уголь
    coal = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Уголь'))

    # Железо
    iron = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Железо'))

    # Бокситы
    bauxite = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Бокситы'))

    # ------vvvvvvv------Нефть на складе------vvvvvvv------
    # Нефть WTI
    wti_oil = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Нефть WTI'))

    # Нефть Brent
    brent_oil = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Нефть Brent'))

    # Нефть Urals
    urals_oil = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Нефть Urals'))

    # ------vvvvvvv------Материалы на складе------vvvvvvv------
    # бензин
    gas = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Бензин'))

    # бензин
    diesel = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Дизельное топливо'))

    # пластик
    plastic = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Пластик'))

    steel = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Сталь'))

    aluminium = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Алюминий'))

    # ------vvvvvvv------Материалы на складе------vvvvvvv------
    # Медикаменты
    medical = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Медикаменты'))
    # Буры
    drilling = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Буровые установки'))

    # ------vvvvvvv------Юниты на складе------vvvvvvv------
    # автоматы
    rifle = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Автоматы'))
    # танки
    tank = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Танки'))
    # штурмовики
    jet = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Штурмовики'))
    # орбитальные орудия
    station = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Орбитальные орудия'))
    # ПЗРК
    pzrk = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'ПЗРК'))
    # AT-cannon
    antitank = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'ПТ-орудия'))
    # Мины
    mines = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Мины'))
    # гаубицы
    ifv = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'БМП'))
    # дроны
    drone = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'БПЛА'))

    def __str__(self):
        return self.storage_from.owner.nickname + " в " + self.storage_from.region.region_name + ": " + str(self.dtime.strftime('%Y-%m-%d %H:%M'))

    # Свойства класса
    class Meta:
        verbose_name = "Лог уничтожения ресурсов"
        verbose_name_plural = "Логи уничтожения"
