# coding=utf-8
from django.db import models
from skill.models.skill import Skill

# Режимное производство
class MilitaryProduction(Skill):

    description = 'Добавляет возможность произвести дополнительные войска при тех же затратах энергии, с округлением затрат в большую сторону'

    requires = [
        {
            'skill': 'knowledge',
            'skill_name': 'Интеллект',
            'level': 40,
        },
        {
            'skill': 'Standardization',
            'skill_name': 'Стандартизация',
            'level': 4,
        },
    ]

    max_level = 4


    class Meta:
        verbose_name = "Режимное производство"
        verbose_name_plural = "Режимное производство"