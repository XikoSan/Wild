# coding=utf-8
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy


# Сторона войны
class WarSide(models.Model):
    # война
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey('content_type', 'object_id')

    # сторона войны
    warSideChoices = (
        ('agr', 'Атака'),
        ('def', 'Оборона'),
    )
    side = models.CharField(
        max_length=3,
        choices=warSideChoices,
        default='agr',
    )

    # Автоматы
    rifle = models.IntegerField(default=0, verbose_name=gettext_lazy('Автоматы'))
    # БМП
    ifv = models.IntegerField(default=0, verbose_name=gettext_lazy('БМП'))

    def __str__(self):
        return 'Сторона войны в ' + getattr(getattr(self.content_object, 'agr_region'), 'region_name')

    # Свойства класса
    class Meta:
        verbose_name = "Сторона войны"
        verbose_name_plural = "Стороны войны"
