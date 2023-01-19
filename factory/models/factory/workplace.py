# coding=utf-8
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy, pgettext_lazy, ugettext as _
from django.apps import apps
from factory.models.factory.workshop import Workshop
from player.actual_manager import ActualStorageManager
from player.player import Player


# Связь игрок - цех
class Workplace(models.Model):
    limit = models.Q(app_label='factory',
                     model='workshop')  # | models.Q(app_label='app', model='b') | models.Q(app_label='app2', model='c')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=limit)
    object_id = models.PositiveIntegerField()
    # Рабочее место - как минимум, Цех фабрики
    content_object = fields.GenericForeignKey('content_type', 'object_id')

    # работник
    worker = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name='Рабочий')

    def __str__(self):

        workplace_class = self.content_type.model_class()

        if workplace_class.objects.filter(pk=self.object_id).exists():
            return self.worker.nickname + ' в ' + str(workplace_class.objects.get(pk=self.object_id))

        else:
            return self.worker.nickname

    # Свойства класса
    class Meta:
        verbose_name = "Работник"
        verbose_name_plural = "Работники"
