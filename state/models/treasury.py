# coding=utf-8
import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy

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
    power_on = models.BooleanField(default=False, verbose_name='Электроскть работает')

    # дата актуализации
    power_actualize = models.DateTimeField(default=None, null=True, blank=True, verbose_name='Акутализация электросети')

    # ------^^^^^^^------Электростанция------^^^^^^^------

    # наличные на складе
    cash = models.BigIntegerField(default=0, verbose_name=gettext_lazy('storage_cash'))

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

    # дизель
    diesel = models.IntegerField(default=0, verbose_name=gettext_lazy('diesel'))

    # пластик
    plastic = models.IntegerField(default=0, verbose_name=gettext_lazy('plastic'))

    # сталь
    steel = models.IntegerField(default=0, verbose_name=gettext_lazy('steel'))

    # алюминий
    aluminium = models.IntegerField(default=0, verbose_name=gettext_lazy('alumunuim'))

    # ------vvvvvvv------Оборудование на складе------vvvvvvv------
    # койки
    medical = models.IntegerField(default=0, verbose_name=gettext_lazy('Койки'))

    # ------vvvvvvv------Юниты на складе------vvvvvvv------
    # Автоматы
    rifle = models.IntegerField(default=0, verbose_name=gettext_lazy('Автоматы'))

    # танки
    tank = models.IntegerField(default=0, verbose_name=gettext_lazy('tank'))

    # штурмовики
    jet = models.IntegerField(default=0, verbose_name=gettext_lazy('attack_air'))

    # орбитальные орудия
    station = models.IntegerField(default=0, verbose_name=gettext_lazy('orb_station'))

    # ПЗРК
    pzrk = models.IntegerField(default=0, verbose_name=gettext_lazy('mpads'))

    # ПТ-пушки
    antitank = models.IntegerField(default=0, verbose_name=gettext_lazy('antitank'))

    # БМП
    ifv = models.IntegerField(default=0, verbose_name=gettext_lazy('ifv'))

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
