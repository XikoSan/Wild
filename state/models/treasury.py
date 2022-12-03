# coding=utf-8
import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy, pgettext_lazy

from region.region import Region
from state.models.state import State
from django.db import transaction

class Treasury(models.Model):
    # государство принадлежности
    state = models.OneToOneField(State, on_delete=models.CASCADE, verbose_name='Государство',
                                 related_name="owner_state")

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    # регион размещения
    region = models.ForeignKey(Region, default=None, null=True, on_delete=models.SET_NULL, blank=True,
                               verbose_name='Регион размещения', related_name="treasury_placement")

    # дата актуализации
    actualize_dtime = models.DateTimeField(default=timezone.now, null=True, blank=True, verbose_name='Дата акутализации')

    # ------vvvvvvv------Электростанция------vvvvvvv------

    # удалено
    power_on = models.BooleanField(default=False, verbose_name='Электросеть работает')

    # дата актуализации
    power_actualize = models.DateTimeField(default=None, null=True, blank=True, verbose_name='Акутализация электросети')

    # ------^^^^^^^------Электростанция------^^^^^^^------

    # наличные на складе
    cash = models.BigIntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Наличные'))

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

    # дизель
    diesel = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Дизельное топливо'))

    # пластик
    plastic = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Пластик'))

    # сталь
    steel = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Сталь'))

    # алюминий
    aluminium = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Алюминий'))

    # ------vvvvvvv------Оборудование на складе------vvvvvvv------
    # Медикаменты
    medical = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Медикаменты'))

    # ------vvvvvvv------Юниты на складе------vvvvvvv------
    # Автоматы
    rifle = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Автоматы'))

    # танки
    tank = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Танки'))

    # штурмовики
    jet = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Штурмовики'))

    # орбитальные орудия
    station = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'Орбитальные орудия'))

    # ПЗРК
    pzrk = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'ПЗРК'))

    # ПТ-пушки
    antitank = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'ПТ-орудия'))

    # БМП
    ifv = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'БМП'))

    # Дроны
    drone = models.IntegerField(default=0, verbose_name=pgettext_lazy('goods', 'БПЛА'))

    # получить Казну с акутализированными значениями запасов
    # любые постоянные траты Казны должны быть прописаны тут
    @staticmethod
    @transaction.atomic
    def get_instance(**params):

        treasury = None
        # получаем запрошенную инстанцию Склада
        if Treasury.objects.filter(**params).exists():
            treasury = Treasury.objects.select_for_update().get(**params)
        else:
            return treasury

        # если дата последней актуализации пуста
        if not treasury.actualize_dtime:
            # запоминаем дату
            treasury.actualize_dtime = timezone.now()

        # инчае если с момента последней актуализации прошла минута
        elif (timezone.now() - treasury.actualize_dtime).total_seconds() >= 60:
            # узнаем сколько раз по минуте прошло
            counts = (timezone.now() - treasury.actualize_dtime).total_seconds() // 60

            # остаток от деления понадобится чтобы указать время обновления
            modulo = (timezone.now() - treasury.actualize_dtime).total_seconds() % 60

            # запоминаем дату
            treasury.actualize_dtime = timezone.now() - datetime.timedelta(seconds=modulo)

        treasury.save()
        return treasury

    def __str__(self):
        return self.state.title

    # Свойства класса
    class Meta:
        verbose_name = "Казна"
        verbose_name_plural = "Казны"
