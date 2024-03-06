# coding=utf-8
from django.db import models
from skill.models.skill import Skill
from django.utils.translation import pgettext_lazy

# Промышленная экскавация
class Excavation(Skill):

    name = pgettext_lazy('skills', 'Промышленная экскавация')
    description = pgettext_lazy('skills', 'позволяет извлекать дополнительные 10% руд за уровень')

    requires = [
        {
            'skill': 'power',
            'skill_name': pgettext_lazy('skills', 'Сила'),
            'level': 10,
        },
        {
            'skill': 'knowledge',
            'skill_name': pgettext_lazy('skills', 'Интеллект'),
            'level': 10,
        },
        {
            'skill': 'endurance',
            'skill_name': pgettext_lazy('skills', 'Выносливость'),
            'level': 10,
        },
    ]

    max_level = 5

    def apply(self, args):

        return args['sum'] * ( 1 + self.level * 0.1 )


    class Meta:
        verbose_name = pgettext_lazy('skills', 'Промышленная экскавация')
        verbose_name_plural = "Промышленная экскавация"