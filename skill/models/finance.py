# coding=utf-8
from django.db import models
from skill.models.skill import Skill

# Промышленная экскавация
class Finance(Skill):

    description = 'позволяет получать двойное финансирование при прохождении прогрессии'

    requires = [
        {
            'skill': 'power',
            'skill_name': 'Сила',
            'level': 25,
        },
        {
            'skill': 'knowledge',
            'skill_name': 'Знания',
            'level': 25,
        },
        {
            'skill': 'endurance',
            'skill_name': 'Выносливость',
            'level': 25,
        },
    ]

    max_level = 1

    def apply(self, args):

        return args['sum'] * ( 1 + self.level * 0.1 )


    class Meta:
        verbose_name = "Подпольное финансирование"
        verbose_name_plural = "Подпольное финансирование"