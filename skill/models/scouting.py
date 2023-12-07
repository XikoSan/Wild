# coding=utf-8
import math
from datetime import timedelta
from django.db import models
from django.utils import timezone

from skill.models.skill import Skill


# Знание местности
# бонус 2% за каждый уровень, если с момента прилёта игрока в регион прошло более суток / 5ур.
class Scouting(Skill):
    description = 'бонус к урону 2% за уровень, если с момента прилёта игрока в регион прошло более суток'

    requires = [
        {
            'skill': 'power',
            'skill_name': 'Сила',
            'level': 15,
        },
        {
            'skill': 'knowledge',
            'skill_name': 'Интеллект',
            'level': 10,
        },
        {
            'skill': 'endurance',
            'skill_name': 'Выносливость',
            'level': 5,
        },
    ]

    max_level = 5

    def apply(self, args):
        if self.player.arrival + timedelta(days=1) < timezone.now():
            return math.floor(args['dmg'] * (1 + self.level * 0.02))

        else:
            return args['dmg']

    class Meta:
        verbose_name = "Знание местности"
        verbose_name_plural = "Знания местности"
