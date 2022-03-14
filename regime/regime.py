# coding=utf-8
from django.db import models


# Абстрактный класс формы правления
# Позволяет создавать формы разных типов
# для получения подклассов  при помощи __subclasses__()
# их надо импортировать в файл вызова
class Regime(object):
    allowed_source = [
        'Temporary',
        'Presidential',
    ]

    allowed_dest = [
        'Temporary',
        'Presidential',
    ]

    government = {
        'leader': False,
        'parliament': False,
        # 'ministry': False,
    }

    # Указание абстрактности класса
    class Meta:
        abstract = True

    @staticmethod
    def set_regime(state):
        return

    @staticmethod
    def set_parliament(state):
        return

    @staticmethod
    def set_leader(current_regime, state):
        return
