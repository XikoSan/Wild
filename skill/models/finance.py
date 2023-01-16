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
            'level': 20,
        },
        {
            'skill': 'knowledge',
            'skill_name': 'Интеллект',
            'level': 20,
        },
        {
            'skill': 'endurance',
            'skill_name': 'Выносливость',
            'level': 20,
        },
    ]

    max_level = 1


    class Meta:
        verbose_name = "Подпольное финансирование"
        verbose_name_plural = "Подпольное финансирование"
        abstract = True
