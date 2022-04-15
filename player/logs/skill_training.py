# coding=utf-8
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy
from django.utils import timezone
from player.logs.log import Log


# запись об изучаемом навыке
class SkillTraining(Log):

    skills_tree = {
        'power':
            {
                'require': None,
            },

        'knowledge':
            {
                'require': None,
            },

        'endurance':
            {
                'require': None,
            },
    }

    #навык
    activityChoices = (
        ('power',  'Сила'),
        ('knowledge',  'Знания'),
        ('endurance',  'Выносливость'),
    )
    skill = models.CharField(
        max_length=20,
        choices=activityChoices,
        blank=True,
        null=True,
        verbose_name='Навык'
    )

    # дата завершения изучения навыка
    end_dtime = models.DateTimeField(default=timezone.now, blank=True,
                                 verbose_name='Время завершения')

    def __str__(self):
        return self.player.nickname + ' изучает ' + str(self.get_skill_display())

    # Свойства класса
    class Meta:
        verbose_name = "Изучаемый навык"
        verbose_name_plural = "Изучаемые навыки"
