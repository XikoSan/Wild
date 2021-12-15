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
    plastic = {
        'title': _('Пластик'),
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
                    'brent_oil': 15,
                },
                {
                    'cash': 10,
                    'urals_oil': 10,
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
                    'coal': 5,
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

    medical = {
        'title': _('medical'),

        'resources':
            [
                {
                    'cash': 5,
                    'plastic': 5,
                    'steel': 2,
                },
            ],

        'time': 10,
        'energy': 1,
    }

    rifle = {
        'title': _('rifle'),

        'resources':
            [
                {
                    'cash': 10,
                    'steel': 1,
                },
            ],

        'time': 3,
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
                    'steel': 2,
                },
            ],

        'time': 10,
        'energy': 1,
    }

    ifv = {
        'title': _('БМП'),

        'resources':
            [
                {
                    'cash': 50,
                    'diesel': 5,
                    'steel': 5,
                },
            ],

        'time': 10,
        'energy': 2,
    }
    # -------------^^^^^^^---------------Производственные схемы---------------^^^^^^^---------------
    schemas = (
        ('gas', gas.get('title')),
        ('diesel', diesel.get('title')),
        ('plastic', diesel.get('title')),

        ('steel', steel.get('title')),
        ('aluminium', aluminium.get('title')),

        ('medical', aluminium.get('title')),

        ('rifle', rifle.get('title')),
        ('tank', tank.get('title')),
        ('jet', jet.get('title')),
        ('pzrk', pzrk.get('title')),
        ('antitank', antitank.get('title')),
        ('ifv', ifv.get('title')),
    )

    type = models.CharField(
        max_length=10,
        choices=schemas,
        verbose_name='Схема',
    )

    # Указание абстрактности класса
    class Meta:
        abstract = True