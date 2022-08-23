# coding=utf-8
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy
from django.utils import timezone
from player.player import Player


# абстрактный навык
# новые навыки добавлять в:
# модель player.skillTraining
class Skill(models.Model):

    description = ''

    requires = []

    # персонаж
    player = models.ForeignKey(Player, default=None, null=True, on_delete=models.CASCADE, verbose_name='Персонаж')

    # текущий уровень
    level = models.IntegerField(default=0, verbose_name='Уровень')

    max_level = 1

    @staticmethod
    def apply(args):
        pass


    @classmethod
    def check_has_right(cls, player):
        has_right = True
        for req in cls.requires:
            if getattr(player, req['skill']) < req['level']:
                has_right = False

        return has_right

    # Указание абстрактности класса
    class Meta:
        abstract = True
