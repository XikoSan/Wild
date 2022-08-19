# coding=utf-8
from django.db import models
from skill.models.skill import Skill

# Промышленная экскавация
class Excavation(Skill):

    description = 'позволяет извлекать дополнительные 10% руд за уровень'

    requires = [
        {
            'skill': 'power',
            'skill_name': 'Сила',
            'level': 10,
        },
        {
            'skill': 'knowledge',
            'skill_name': 'Знания',
            'level': 10,
        },
        {
            'skill': 'endurance',
            'skill_name': 'Выносливость',
            'level': 10,
        },
    ]

    max_level = 5

    def apply(self, args):

        return args['sum'] * ( 1 + self.level * 0.1 )


    class Meta:
        verbose_name = "Промышленная экскавация"
        verbose_name_plural = "Промышленная экскавация"