# coding=utf-8
import datetime
from django.db import models
from django.utils.translation import gettext_lazy
from django.utils.translation import ugettext as _

from player.player import Player
from region.region import Region
from storage.models.storage import Storage
from storage.models.trading_log import TradingLog


# Торговое предложение (Ордер)
class TradeOffer(models.Model):
    # # разместивший предложение
    # owner = models.ForeignKey(Player, default=None, null=True, on_delete=models.CASCADE, blank=True,
    #                            verbose_name='Разместивший ордер', related_name="offer_owner")
    # склад разместившего предложение
    owner_storage = models.ForeignKey(Storage, default=None, null=True, on_delete=models.CASCADE, blank=True,
                                      verbose_name='Склад разместившего', related_name="offer_storage")

    # количество товара изначально
    initial_volume = models.BigIntegerField(default=0, verbose_name='Количество изначально')
    # количество товара
    count = models.BigIntegerField(default=0, verbose_name='Количество')
    # цена товара
    price = models.BigIntegerField(default=0, verbose_name='Цена')

    # стоимость товара, при скупке
    # то есть сумма, которая лежала в скупке изначально
    cost = models.BigIntegerField(default=0, verbose_name='Стоимость закупки')
    # количество денег, которые остались в закупке
    # в отличии от CashLock, хранит в себе оставшуюся сумму денег, даже если предложение было отменено
    # из CashLock же деньги возвращаются на счет
    cost_count = models.BigIntegerField(default=0, verbose_name='Осталось денег в закупке')

    # принявшие предложение
    accepters = models.ManyToManyField(TradingLog, blank=True,
                                       verbose_name='Принявшие ордер',
                                       related_name="offer_accepters")

    # тип ордера
    sell = 'sell'
    buy = 'buy'
    offerTypeChoices = (
        (sell, 'Продажа'),
        (buy, 'Покупка'),
    )
    type = models.CharField(
        max_length=4,
        choices=offerTypeChoices,
        default=sell,
    )

    # доступность ордера
    all = 'all'
    state = 'state'
    party = 'party'
    offerViewChoices = (
        (all, 'Все'),
        (state, 'Государство'),
        (party, 'party'),
    )
    view_type = models.CharField(
        max_length=6,
        choices=offerViewChoices,
        default=all,
    )

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
        ('steel', 'Сталь'),
        ('aluminium', 'Алюминий'),

        ('tank', 'Танки'),
        ('antitank', 'ПТ-орудия'),
        ('station', 'Орбитальные орудия'),
        ('jet', 'Штурмовики'),
        ('pzrk', 'ПЗРК')
    )

    good = models.CharField(
        max_length=10,
        choices=goodsChoises,
        default=sell,
    )

    # время создания предложения
    create_date = models.DateTimeField(default=None, null=True, blank=True)
    # время закрытия предложения
    accept_date = models.DateTimeField(default=None, null=True, blank=True)

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    def __str__(self):
        rettype = None
        if self.type == 'sell':
            rettype = ' продаёт '
        else:
            rettype = ' покупает '
        return self.owner_storage.owner.nickname + ' ' + str(
            self.create_date.strftime('%Y-%m-%d %H:%M')) + rettype + self.get_good_display()

    # Свойства класса
    class Meta:
        verbose_name = "Торговый ордер"
        verbose_name_plural = "Торговые ордера"
