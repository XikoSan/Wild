from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from ava_border.models.ava_border import AvaBorder
from player.player import Player


class AvaBorderOwnership(models.Model):
    # Показатель того, что игрок использует рамку
    in_use = models.BooleanField(default=False, null=False, verbose_name='Используется')

    # набор стикеров
    owner = models.ForeignKey(Player, on_delete=models.CASCADE, blank=False,
                              verbose_name='Игрок')

    # набор стикеров
    border = models.ForeignKey(AvaBorder, on_delete=models.CASCADE, blank=False,
                               verbose_name='Рамка')

    # Показывать PNG рамку, вместо SVG
    png_use = models.BooleanField(default=False, null=False, verbose_name='PNG')

    def __str__(self):
        return self.border.title

    # Свойства класса
    class Meta:
        verbose_name = "Владелец рамки"
        verbose_name_plural = "Владельцы рамок"


# сигнал прослушивающий создание
@receiver(post_save, sender=AvaBorderOwnership)
def save_post(sender, instance, created, **kwargs):
    if instance.in_use:
        AvaBorderOwnership.objects.filter(owner=instance.owner).exclude(pk=instance.pk).update(in_use=False)
