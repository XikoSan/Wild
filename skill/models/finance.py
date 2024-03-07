# coding=utf-8
from django.db import models
from skill.models.skill import Skill
from django.utils.translation import pgettext_lazy

# Подпольное финансирование
class Finance(Skill):

    name = pgettext_lazy('skills', "Подпольное финансирование")
    description = pgettext_lazy('skills', 'позволяет получать двойное финансирование при прохождении прогрессии')

    requires = [
        {
            'skill': 'power',
            'skill_name': pgettext_lazy('skills', 'Сила'),
            'level': 20,
        },
        {
            'skill': 'knowledge',
            'skill_name': pgettext_lazy('skills', 'Интеллект'),
            'level': 20,
        },
        {
            'skill': 'endurance',
            'skill_name': pgettext_lazy('skills', 'Выносливость'),
            'level': 20,
        },
    ]

    max_level = 1


    class Meta:
        verbose_name = pgettext_lazy('skills', "Подпольное финансирование")
        verbose_name_plural = "Подпольное финансирование"
        abstract = True
