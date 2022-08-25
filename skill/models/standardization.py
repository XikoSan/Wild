# coding=utf-8
from django.db import models
from skill.models.skill import Skill

# Стандартизация
class Standardization(Skill):

    description = 'Добавляет возможность произвести дополнительный товар при тех же затратах энергии, с округлением затрат в большую сторону'

    requires = [
        {
            'skill': 'knowledge',
            'skill_name': 'Интеллект',
            'level': 25,
        },
    ]

    max_level = 4


    class Meta:
        verbose_name = "Стандартизация"
        verbose_name_plural = "Стандартизация"