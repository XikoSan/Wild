# coding=utf-8
from django.db import models
from skill.models.skill import Skill
from django.utils.translation import pgettext_lazy

# Режимное производство
class MilitaryProduction(Skill):

    name = pgettext_lazy('skills', "Режимное производство")
    description = pgettext_lazy('skills', 'Добавляет возможность произвести дополнительные войска при тех же затратах энергии, с округлением затрат в большую сторону')

    requires = [
        {
            'skill': 'knowledge',
            'skill_name': pgettext_lazy('skills', 'Интеллект'),
            'level': 40,
        },
        {
            'skill': 'Standardization',
            'skill_name': pgettext_lazy('skills', 'Стандартизация'),
            'level': 4,
        },
    ]

    max_level = 4


    class Meta:
        verbose_name = pgettext_lazy('skills', "Режимное производство")
        verbose_name_plural = "Режимное производство"