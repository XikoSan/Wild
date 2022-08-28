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
                    'cash': 5,
                    'wti_oil': 10,
                },
                {
                    'cash': 8,
                    'brent_oil': 15,
                },
                {
                    'cash': 8,
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
                    'cash': 8,
                    'wti_oil': 15,
                },
                {
                    'cash': 5,
                    'brent_oil': 10,
                },
                {
                    'cash': 8,
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
                    'cash': 8,
                    'wti_oil': 15,
                },
                {
                    'cash': 8,
                    'brent_oil': 15,
                },
                {
                    'cash': 5,
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
                    'cash': 5,
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
                    'cash': 5,
                    'bauxite': 20,
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
                    'cash': 25,
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
                    'cash': 30,
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
                    'cash': 30,
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

    drone = {
        'title': _('БПЛА'),

        'resources':
            [
                {
                    'cash': 10,
                    'gas': 1,
                    'aluminium': 5,
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
        ('drone', drone.get('title')),
    )

    type = models.CharField(
        max_length=10,
        choices=schemas,
        verbose_name='Схема',
    )

    # Указание абстрактности класса
    class Meta:
        abstract = True