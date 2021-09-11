# coding=utf-8
import datetime
from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _


# Абстрактный класс задачи на производство
# Позволяет создавать личные и фабричные задачи на производство при общей механике создания их на вкладке "Производство"
class Project(models.Model):
    # признак того что производство идет сейчас
    running = models.BooleanField(default=False, verbose_name='Производится')
    # -------------vvvvvvv---------------Производственные схемы---------------vvvvvvv---------------
    gas = {
        'title': _('Бензин'),
        # 'title': _('gas'),

        'resources':
            [
                {
                    'cash': 10,
                    'wti_oil': 10,
                },
                {
                    'cash': 10,
                    'brent_oil': 15,
                },
                {
                    'cash': 10,
                    'urals_oil': 15,
                },
            ],

        'time': 10,
        'energy': 1,
    }
    # plastic = {
    #     'title': _('Пластик'),
    #     # 'title': _('plastic'),
    #
    #     'resources':
    #         {
    #             {
    #                 'cash': 10,
    #                 'wti_oil': 15,
    #             },
    #             {
    #                 'cash': 10,
    #                 'brent_oil': 10,
    #             },
    #             {
    #                 'cash': 10,
    #                 'urals_oil': 15,
    #             },
    #         },
    #     'time': 10,
    #     'energy': 1,
    # }
    diesel = {
        'title': _('Дизель'),
        # 'title': _('plastic'),

        'resources':
            [
                {
                    'cash': 10,
                    'wti_oil': 15,
                },
                {
                    'cash': 10,
                    'brent_oil': 10,
                },
                {
                    'cash': 10,
                    'urals_oil': 15,
                },
            ],

        'time': 10,
        'energy': 1,
    }
    steel = {
        'title': _('steel'),

        'resources':
            [
                {
                    'cash': 10,
                    'iron': 10,
                },
            ],

        'time': 10,
        'energy': 1,
    }

    aluminium = {
        'title': _('aluminium'),

        'resources':
            [
                {
                    'cash': 10,
                    'bauxite': 10,
                },
            ],

        'time': 10,
        'energy': 1,
    }

    tank = {
        'title': _('tank'),

        'resources':
            [
                {
                    'cash': 100,
                    'gas': 5,
                    'steel': 15,
                },
            ],

        'time': 30,
        'energy': 1,
    }

    jet = {
        'title': _('attack_air'),

        'resources':
            [
                {
                    'cash': 150,
                    'aluminium': 15,
                    'gas': 5,
                },
            ],

        'time': 45,
        'energy': 1,
    }

    pzrk = {
        'title': _('mpads'),

        'resources':
            [
                {
                    'cash': 50,
                    'gas': 5,
                    'steel': 2,
                },
            ],

        'time': 10,
        'energy': 1,
    }

    antitank = {
        'title': _('antitank'),

        'resources':
            [
                {
                    'cash': 50,
                    'gas': 2,
                    'steel': 5,
                },
            ],

        'time': 10,
        'energy': 1,
    }
    # -------------^^^^^^^---------------Производственные схемы---------------^^^^^^^---------------
    schemas = (
        ('gas', gas.get('title')),
        ('diesel', diesel.get('title')),
        ('steel', steel.get('title')),
        ('aluminium', aluminium.get('title')),
        ('tank', tank.get('title')),
        ('jet', jet.get('title')),
        ('pzrk', pzrk.get('title')),
        ('antitank', antitank.get('title')),
    )

    type = models.CharField(
        max_length=10,
        choices=schemas,
        verbose_name='Схема',
    )

    count = models.IntegerField(default=0, verbose_name='Количество')

    # время постановки на производство
    prod_start = models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), blank=True,
                                      verbose_name='Время начала производства')
    # плановое время завершения производства
    prod_end_plan = models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), blank=True, null=True,
                                         verbose_name='Плановое время завершения производства')
    # фактическое время завершения производства
    prod_end_fact = models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), blank=True, null=True,
                                         verbose_name='Время завершения производства')

    # id фонового процесса данного производства
    task_id = models.CharField(max_length=150, blank=True, null=True, verbose_name='id фонового процесса')

    # Указание абстрактности класса
    class Meta:
        abstract = True

    # проверить наличие ресурсов
    def validateProject(self):
        return

    # рассчитать время производства
    def timeCalculation(self):
        return

    # выполнить производственную задачу
    def doProject(self):
        return
