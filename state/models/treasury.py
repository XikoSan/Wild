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
    # регион размещения
    region = models.ForeignKey(Region, default=None, null=True, on_delete=models.SET_NULL, blank=True,
                               verbose_name='Регион размещения', related_name="treasury_placement")

    steel = models.IntegerField(default=0, verbose_name=gettext_lazy('steel'))

    # # получить информацию о количестве предметов
    # def allTreasuryCount(self):
    #     data = {}
    #     data['gold'] = getattr(self, 'gold')
    #     # for mode in {'resourses', 'materials', 'units'}:
    #     for unit in getattr(Storage, 'resourses').keys():
    #         data[unit] = getattr(self, unit)
    #
    #     return data
    #
    # # начислить предметы на Склад
    # def unitsToTreasuryAdd(self, request, mode):
    #     data_dict = {}
    #     for unit in getattr(Storage, mode).keys():
    #         # проверяем что передано целое положительное число
    #         try:
    #             unit_cnt = int(request.POST.get(unit, ''))
    #             # передано отрицательное число
    #             if unit_cnt < 0:
    #                 return
    #             # записываем новое число предметов на складе
    #             if unit == 'cash':
    #                 data_dict['gold'] = getattr(self, 'gold') + unit_cnt
    #             else:
    #                 data_dict[unit] = getattr(self, unit) + unit_cnt
    #
    #         # нет юнита в запросе, ищем дальше
    #         except ValueError:
    #             continue
    #     # начисляем предметы
    #     Treasury.objects.filter(pk=self.pk).update(**data_dict)

    def __str__(self):
        return self.state.title

    # Свойства класса
    class Meta:
        verbose_name = "Казна"
        verbose_name_plural = "Казны"
