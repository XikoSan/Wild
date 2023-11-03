# coding=utf-8
from django.db import models
from skill.models.skill import Skill

# Гидроразрыв
class Fracturing(Skill):

    description = 'позволяет извлекать дополнительные 10% нефти за уровень'

    requires = [
        {
            'skill': 'knowledge',
            'skill_name': 'Интеллект',
            'level': 15,
        },
        {
            'skill': 'endurance',
            'skill_name': 'Выносливость',
            'level': 15,
        },
    ]

    max_level = 5

    def apply(self, args):

        return args['sum'] * ( 1 + self.level * 0.1 )


    class Meta:
        verbose_name = "Гидроразрыв"
        verbose_name_plural = "Гидроразрыв"