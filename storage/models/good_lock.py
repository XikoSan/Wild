# coding=utf-8
import datetime
from django.db import models
from django.utils.translation import gettext_lazy
from django.utils.translation import ugettext as _

from player.player import Player
from region.models.region import Region
from storage.models.storage import Storage
from storage.models.trade_offer import TradeOffer
from player.actual_manager import ActualManager
from storage.models.good import Good


# Блокировки ресурсов на Складе, при их проадже
class GoodLock(models.Model):
    objects = models.Manager()  # Менеджер по умолчанию
    actual = ActualManager()  # Менеджер активных записей

    # склад блокировки
    lock_storage = models.ForeignKey(Storage, default=None, on_delete=models.CASCADE,
                                     verbose_name='Склад блокировки', related_name="lock_storage")

    # товар
    goodsChoises = (
        ('coal', 'Уголь'),
        ('iron', 'Железо'),
        ('bauxite', 'Бокситы'),

        ('wti_oil', 'Нефть WTI'),
        ('brent_oil', 'Нефть Brent'),
        ('urals_oil', 'Нефть Urals'),

        ('gas', 'Бензин'),
        ('diesel', 'Дизельное топливо'),
        ('plastic', 'Пластик'),
        ('steel', 'Сталь'),
        ('aluminium', 'Алюминий'),

        ('medical', 'Медикаменты'),
        ('drilling', 'Буровые установки'),

        ('rifle', 'Автоматы'),
        ('tank', 'Танки'),
        ('antitank', 'ПТ-орудия'),
        ('mines', 'Мины'),
        ('station', 'Орбитальные орудия'),
        ('jet', 'Штурмовики'),
        ('pzrk', 'ПЗРК'),
        ('ifv', 'БМП'),
        ('drone', 'Дроны')
    )

    old_good = models.CharField(
        max_length=10,
        choices=goodsChoises,
        default=None,
        null=True, blank=True,
    )

    lock_good =  models.ForeignKey(Good, default=None, on_delete=models.CASCADE,
                                     verbose_name='Товар', related_name="lock_good")

    lock_count = models.BigIntegerField(default=0, verbose_name='Количество')

    lock_offer = models.ForeignKey(TradeOffer, default=None, on_delete=models.CASCADE,  null=True, blank=True,
                                   verbose_name='Торговое предложение', related_name="good_lock_offer")

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    def __str__(self):
        return 'Склад ' + self.lock_storage.owner.nickname + ' в ' + \
               self.lock_storage.region.region_name + ': ' + str(self.lock_count) + ' ' + self.lock_good.name

    # Свойства класса
    class Meta:
        verbose_name = "Блокировка ресурсов"
        verbose_name_plural = "Блокировки ресурсов"
