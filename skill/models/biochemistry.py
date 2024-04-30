# coding=utf-8
from django.db import models
from skill.models.skill import Skill
from django.utils.translation import pgettext_lazy

# Биохимия
class Biochemistry(Skill):

    name = pgettext_lazy('skills', "Биохимия")
    description = pgettext_lazy('skills', 'Открывает возможность производства бустеров Характеристик')

    requires = [
        {
            'skill': 'knowledge',
            'skill_name': pgettext_lazy('skills', 'Интеллект'),
            'level': 50,
        },
        {
            'skill': 'power',
            'skill_name': pgettext_lazy('skills', 'Сила'),
            'level': 10,
        },
        {
            'skill': 'endurance',
            'skill_name': pgettext_lazy('skills', 'Выносливость'),
            'level': 10,
        },
    ]

    max_level = 1


    class Meta:
        verbose_name = pgettext_lazy('skills', "Биохимия")
        verbose_name_plural = "Биохимия"