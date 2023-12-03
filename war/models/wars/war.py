# coding=utf-8
from django.db import models
from django_celery_beat.models import PeriodicTask

from region.models.region import Region


# класс абстрактной войны
class War(models.Model):
    squads_dict = {
        'infantry': 'Пехота',
        'lightvehicle': 'Легкая бронетехника',
        'heavyvehicle': 'Тяжелая бронетехника',
        'recon': 'Разведка'
    }

    # прочность укрепов на старте
    defence_points = models.BigIntegerField(default=0, verbose_name='Прочность Укрепов')

    # признак того что война идет сейчас
    running = models.BooleanField(default=False, verbose_name='Идёт война')
    # раунд войны
    round = models.IntegerField(default=0, verbose_name='Раунд войны')

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

    # таска
    task = models.OneToOneField(PeriodicTask, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(class)s_round_task")

    # таска завершения войны
    end_task = models.OneToOneField(PeriodicTask, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(class)s_end_task")

    # поминутный график боя
    graph = models.TextField(default='', null=True, blank=True, verbose_name='График боя')

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

    def get_page(self, request):
        pass
