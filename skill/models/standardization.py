# coding=utf-8
from django.db import models
from skill.models.skill import Skill
from django.utils.translation import pgettext_lazy

# Стандартизация
class Standardization(Skill):

    name = pgettext_lazy('skills', "Стандартизация")
    description = pgettext_lazy('skills', 'Добавляет возможность произвести дополнительные материалы при тех же затратах энергии, с округлением затрат в большую сторону')

    requires = [
        {
            'skill': 'knowledge',
            'skill_name': pgettext_lazy('skills', 'Интеллект'),
            'level': 25,
        },
    ]

    max_level = 4


    class Meta:
        verbose_name = pgettext_lazy('skills', "Стандартизация")
        verbose_name_plural = "Стандартизация"