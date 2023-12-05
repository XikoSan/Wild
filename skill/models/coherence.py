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

        total_units = 0
        types_count = 0

        for unit in args['units'].keys():
            total_units += int(args['units'][unit])
            types_count += 1

        bonus = 0

        if types_count > 1:
            # теперь считаем сколько типов юнитов имеют больше 20%
            types_count = 0
            for unit in args['units'].keys():
                if int(args['units'][unit]) * 100 / total_units >= 20:
                    bonus += 0.1
                    types_count += 1

            if types_count > 1:
                return math.floor(args['dmg'] * (1 + bonus))
            else:
                return args['dmg']
        else:
            return args['dmg']

    class Meta:
        verbose_name = "Слаженность"
        verbose_name_plural = "Слаженность"
