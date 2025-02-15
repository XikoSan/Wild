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

    # Очки урона
    count = models.IntegerField(default=0, verbose_name='Очки урона')

    def __str__(self):
        # if self.content_object is not None:
        return 'Сторона войны'
        # else:
        # return 'Сторона войны'

    # Свойства класса
    class Meta:
        verbose_name = "Сторона войны"
        verbose_name_plural = "Стороны войны"
