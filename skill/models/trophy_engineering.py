# coding=utf-8
from django.db import models
from skill.models.skill import Skill
from django.utils.translation import pgettext_lazy

# Трофейная инженерия
class TrophyEngineering(Skill):

    name = pgettext_lazy('skills', "Трофейная инженерия")
    description = pgettext_lazy('skills', 'Открывает возможность конвертации оружия в трофейные образцы')

    requires = [
        {
            'skill': 'knowledge',
            'skill_name': pgettext_lazy('skills', 'Интеллект'),
            'level': 90,
        },
        {
            'skill': 'power',
            'skill_name': pgettext_lazy('skills', 'Сила'),
            'level': 30,
        },
        {
            'skill': 'endurance',
            'skill_name': pgettext_lazy('skills', 'Выносливость'),
            'level': 50,
        },
    ]

    max_level = 1


    class Meta:
        verbose_name = pgettext_lazy('skills', "Трофейная инженерия")
        verbose_name_plural = "Трофейная инженерия"