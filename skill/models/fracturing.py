# coding=utf-8
from django.db import models
from skill.models.skill import Skill
from django.utils.translation import pgettext_lazy

# Гидроразрыв
class Fracturing(Skill):

    name = pgettext_lazy('skills', "Гидроразрыв")
    description = pgettext_lazy('skills', 'позволяет извлекать дополнительные 10% нефти за уровень')

    requires = [
        {
            'skill': 'knowledge',
            'skill_name': pgettext_lazy('skills', 'Интеллект'),
            'level': 15,
        },
        {
            'skill': 'endurance',
            'skill_name': pgettext_lazy('skills', 'Выносливость'),
            'level': 15,
        },
    ]

    max_level = 5

    def apply(self, args):

        return args['sum'] * ( 1 + self.level * 0.1 )


    class Meta:
        verbose_name = pgettext_lazy('skills', "Гидроразрыв")
        verbose_name_plural = "Гидроразрыв"