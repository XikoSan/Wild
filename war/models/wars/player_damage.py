# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy
from storage.models.good import Good
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from player.player import Player
from region.models.region import Region


# Урон, нанесённый игроками в войнах
class PlayerDamage(models.Model):
    # война
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey('content_type', 'object_id')

    # игрок
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name='Игрок')

    # Скрывать в списке
    hide = models.BooleanField(default=False, null=False, verbose_name='Скрыто')

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
    damage = models.IntegerField(default=0, verbose_name='Урон')

    # Затраты энергии
    energy = models.IntegerField(default=0, verbose_name='Энергии потрачено')

    def __str__(self):
        return f"{self.get_side_display()}: {self.player.nickname} нанёс {self.damage}"

    # Свойства класса
    class Meta:
        verbose_name = "Урон игрока"
        verbose_name_plural = "Урон игроков"
