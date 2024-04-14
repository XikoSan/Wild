# coding=utf-8
from django.db import models
from django.utils.translation import gettext_lazy, pgettext_lazy, ugettext as _
from django.apps import apps
from player.player import Player
from django import forms
from django.utils.html import mark_safe


# Владелец самолёта
class Plane(models.Model):

    # Показатель того, что игрок использует
    in_use = models.BooleanField(default=False, null=False, verbose_name='Используется')

    # владелец склада
    player = models.ForeignKey(Player, default=None, null=True, on_delete=models.CASCADE, verbose_name='Владелец')



    planes = {
        'pretender': ['base', 'green' ],
        'trickster': ['base' ],
        'smuggler': ['base' ],
        'chaser': ['base', 'black' ],
        'nagger': ['base', ],
        'reaper': ['base', 'black' ],
        'cheater': ['base',
                    'red', 'yellow', 'orange',
                    'green', 'dark_blue', 'light_blue',
                    'pink', 'violet', 'black',
                    'green_cam', 'blue_cam', 'desert_cam'],
        'carrier': ['base', 'pink', ],
        'observer': ['base', ],
    }

    # самолёт
    planesChoices = (
                        ('nagger', 'Nagger'),
                        ('pretender', 'Pretender'),
                        ('trickster', 'Trickster'),
                        ('smuggler', 'Smuggler'),
                        ('chaser', 'Chaser'),
                        ('reaper', 'Reaper'),
                        ('cheater', 'Cheater'),
                        ('carrier', 'Carrier'),
                        ('observer', 'Observer'),
                    )

    colorChoices = (
                        ('base', 'базовый'),
                        ('red', 'красный'),
                        ('orange', 'оранжевый'),
                        ('yellow', 'желтый'),
                        ('green', 'зелёный'),
                        ('light_blue', 'голубой'),
                        ('dark_blue', 'синий'),
                        ('violet', 'фиолетовый'),
                        ('pink', 'розовый'),
                        ('black', 'чёрный'),
                        ('green_cam', 'зелёный камуфляж'),
                        ('blue_cam', 'синий камуфляж'),
                        ('desert_cam', 'песочный камуфляж'),
                    )

    plane = models.CharField(
        max_length=10,
        choices=planesChoices,
    )

    color = models.CharField(
        max_length=10,
        choices=colorChoices,
    )

    def image_tag(self):
        if self.plane:
            return mark_safe(f'<img src="/static/img/planes/{ self.plane }/{ self.plane }_{ self.color }.svg" width="150" height="150" />')
        else:
            return mark_safe(f'<img src="/static/img/planes/pretender/pretender_1.svg" width="150" height="150" />')

    image_tag.short_description = 'Image'
    image_tag.allow_tags = True

    def clean(self):
        if not self.color in self.planes[self.plane]:
            raise forms.ValidationError(f'Самолёт {self.plane} не имеет окраски {self.get_color_display()}!')

    def __str__(self):
        return f'{self.plane} {self.get_color_display()} игрока {self.player.nickname}'

    # Свойства класса
    class Meta:
        verbose_name = "Самолёт"
        verbose_name_plural = "Самолёты"
