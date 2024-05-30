# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy, pgettext_lazy, ugettext as _
from django.apps import apps
from player.player import Player
from django import forms
from django.utils.html import mark_safe
from region.models.plane import Plane


# дроп из лутбокса. Можно заменить или забрать
class LootboxPrize(models.Model):

    # удалено
    deleted = models.BooleanField(default=False, null=False, verbose_name='Удалено')
    # заменено
    replaced = models.BooleanField(default=False, null=False, verbose_name='Заменено')

    # владелец склада
    player = models.ForeignKey(Player, default=None, null=True, on_delete=models.CASCADE, verbose_name='Владелец')

    plane = models.CharField(
        max_length=10,
        choices=Plane.planesChoices,
    )

    color = models.CharField(
        max_length=20,
        choices=Plane.colorChoices,
    )

    def image_tag(self):
        if self.plane:
            return mark_safe(f'<img src="/static/img/planes/{ self.plane }/{ self.plane }_{ self.color }.svg" width="150" height="150" />')
        else:
            return mark_safe(f'<img src="/static/img/planes/pretender/pretender_1.svg" width="150" height="150" />')

    image_tag.short_description = 'Image'
    image_tag.allow_tags = True

    def clean(self):
        if not self.color in Plane.planes[self.plane]:
            raise forms.ValidationError(f'Самолёт {self.plane} не имеет окраски {self.get_color_display()}!')

    def __str__(self):
        return f'{self.plane} {self.get_color_display()} игрока {self.player.nickname}'

    # Свойства класса
    class Meta:
        verbose_name = "Наградные самолёты"
        verbose_name_plural = "Наградные самолёты"
