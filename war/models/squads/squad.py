# coding=utf-8
from django.contrib.contenttypes import fields
# from war.models.wars
from django.contrib.contenttypes.models import ContentType
from django.db import models

from player.player import Player


# отряд армии игрока
class Squad(models.Model):
    # владелец отряда
    owner = models.ForeignKey(Player, default=None, null=True, on_delete=models.SET_NULL, verbose_name='Владелец',
                              related_name='squad_owner')

    # война
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey('content_type', 'object_id')

    # сторона войны
    squadSideChoices = (
        ('agr', 'Атака'),
        ('def', 'Оборона'),
    )
    side = models.CharField(
        max_length=3,
        choices=squadSideChoices,
        default='agr',
    )

    # время ввода первого юнита отряда в бой
    deploy = models.DateTimeField(default=None, blank=True, null=True, verbose_name='Ввод в бой')
    # время уничтожения отряда (после этого создается новый)
    destroy = models.DateTimeField(default=None, blank=True, null=True, verbose_name='Уничтожение')

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    # Указание абстрактности класса
    class Meta:
        abstract = True
