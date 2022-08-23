# coding=utf-8
from django.db import models
from skill.models.skill import Skill

# Стандартизация
class Standardization(Skill):

    description = 'Добавляет возможность произвести дополнительную единицу товара за единицу энергии, с округлением затрат в большую сторону'

    requires = [
        {
            'skill': 'knowledge',
            'skill_name': 'Знания',
            'level': 25,
        },
    ]

    max_level = 4


    class Meta:
        verbose_name = "Стандартизация"
        verbose_name_plural = "Стандартизация"