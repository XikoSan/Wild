# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy, pgettext_lazy, ugettext as _

from player.actual_manager import ActualStorageManager
from factory.models.factory.factory import Factory
from factory.models.project import Project


# Цех частной фабрики
class Workshop(models.Model):

    # фабрика
    factory = models.ForeignKey(Factory, default=None, on_delete=models.CASCADE, verbose_name='Фабрика')

    # производимый товар
    good = models.CharField(
        max_length=20,
        choices=Project.schemas,
        default=None,
        verbose_name='Товар',
    )

    def __str__(self):
        good_text = None
        for schema in Project.schemas:
            if self.good == schema[0]:
                good_text = schema[1]

        return self.factory.title + ": " + str(good_text)

    # Свойства класса
    class Meta:
        verbose_name = "Цех"
        verbose_name_plural = "Цеха"
