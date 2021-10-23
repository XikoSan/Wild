# coding=utf-8
import sys
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.utils.translation import gettext_lazy, ugettext as _
from io import BytesIO

from region.region import Region
from state.models.state import State
from storage.models.storage import Storage


class Treasury(models.Model):
    # государство принадлежности
    state = models.OneToOneField(State, on_delete=models.CASCADE, verbose_name='Государство',
                                 related_name="owner_state")

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    # регион размещения
    region = models.ForeignKey(Region, default=None, null=True, on_delete=models.SET_NULL, blank=True,
                               verbose_name='Регион размещения', related_name="treasury_placement")

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

    # сталь
    steel = models.IntegerField(default=0, verbose_name=gettext_lazy('steel'))

    # алюминий
    aluminium = models.IntegerField(default=0, verbose_name=gettext_lazy('alumunuim'))

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

    def __str__(self):
        return self.state.title

    # Свойства класса
    class Meta:
        verbose_name = "Казна"
        verbose_name_plural = "Казны"
