# coding=utf-8
from django.db import models
from django_celery_beat.models import PeriodicTask

from region.region import Region


# класс абстрактной войны
class War(models.Model):
    squads_dict = {
        'infantry': 'Пехота',
        'lightvehicle': 'Легкая бронетехника',
        'heavyvehicle': 'Тяжелая бронетехника',
        'recon': 'Разведка'
    }
    # признак того что война идет сейчас
    running = models.BooleanField(default=False, verbose_name='Идёт война')
    # раунд войны
    round = models.IntegerField(default=0, verbose_name='Раунд войны')
    # баланс разведки
    recon_balance = models.FloatField(default=1, verbose_name='Баланс разведки')

    # время начала войны
    start_time = models.DateTimeField(default=None, blank=True, null=True, verbose_name='Начало войны')
    # время окончания войны
    end_time = models.DateTimeField(default=None, blank=True, null=True, verbose_name='Конец войны')

    # регион-агрессор
    agr_region = models.ForeignKey(Region, default=None, null=True, on_delete=models.SET_NULL, blank=True,
                                   verbose_name='Регион-агрессор', related_name="%(class)s_agr_region")
    # регион обороняющихся
    def_region = models.ForeignKey(Region, default=None, null=True, on_delete=models.SET_NULL, blank=True,
                                   verbose_name='Регион обороняющихся', related_name="%(class)s_def_region")

    # урон - атакующие
    agr_dmg = models.BigIntegerField(default=0, verbose_name='Урон - атакующие')

    # описание последнего раунда
    round_log = models.TextField(default='', null=True, blank=True, verbose_name='Последний раунд')

    # таска
    task = models.OneToOneField(PeriodicTask, on_delete=models.SET_NULL, null=True, blank=True)

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    # Указание абстрактности класса
    class Meta:
        abstract = True

    # просчитать раунд войны
    def war_round(self):
        pass

    # завершить войну
    def war_end(self):
        pass

    def get_attrs(self):
        pass
