# coding=utf-8
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy
from django.utils import timezone
from player.logs.log import Log
from player.views.get_subclasses import get_subclasses
from skill.models.skill import Skill
from skill.models.excavation import Excavation
# from skill.models.finance import Finance
from skill.models.standardization import Standardization

# запись об изучаемом навыке
# новые классы навыков надо импортировать сюда
class SkillTraining(Log):

    skill_classes = get_subclasses(Skill)

    #навык
    activityChoices = (
        ('power',  'Сила'),
        ('knowledge',  'Знания'),
        ('endurance',  'Выносливость'),
    )

    for skill_cl in skill_classes:
        activityChoices = activityChoices + ((skill_cl.__name__, skill_cl._meta.verbose_name_raw),)

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
