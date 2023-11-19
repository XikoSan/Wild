# coding=utf-8
import math
from datetime import timedelta
from django.db import models
from django.utils import timezone

from skill.models.skill import Skill


# Слаженность
# бонус 10% за каждый вид юнитов, количество которых в отряде не менее 20%
class Coherence(Skill):
    description = 'бонус 10% за каждый вид юнитов, количество которых в отряде не менее 20%'

    requires = [
        {
            'skill': 'power',
            'skill_name': 'Сила',
            'level': 30,
        },
        {
            'skill': 'knowledge',
            'skill_name': 'Интеллект',
            'level': 15,
        },
    ]

    max_level = 1

    def apply(self, args):
        pass
        # if self.player.arrival + timedelta(days=1) < timezone.now():
        #     if not 'not_floor' in args:
        #         return math.floor(args['sum'] * (1 + self.level * 0.02))
        #     else:
        #         return args['sum'] * (1 + self.level * 0.02)
        #
        # else:
        #     return args['sum']

    class Meta:
        verbose_name = "Слаженность"
        verbose_name_plural = "Слаженность"
