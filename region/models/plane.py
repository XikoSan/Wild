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

        'nagger': ['base', 'black_gold', 'dreamflight' ],

        'pretender': ['base',
                      'red', 'yellow', 'orange',
                      'green', 'dark_blue', 'light_blue',
                      'pink', 'violet', 'black',
                      'wood',
                      ],

        'trickster': ['base',
                      'red', 'yellow', 'orange',
                      'green', 'dark_blue', 'light_blue',
                      'pink', 'violet', 'black',
                      'gold'
                      ],

        'smuggler': ['base',
                     'red', 'yellow', 'orange',
                     'green', 'dark_blue', 'light_blue',
                     'violet',
                     ],

        'chaser': ['base', 'black' ],

        'reaper': ['base',
                   'red', 'yellow', 'orange',
                   'green', 'dark_blue', 'light_blue',
                   'pink', 'violet', 'black',
                   'airball',
                   'gold' ],

        'cheater': ['base',
                    'red', 'yellow', 'orange',
                    'green', 'dark_blue', 'light_blue',
                    'pink', 'violet', 'black',
                    'gold',
                    'green_cam', 'blue_cam', 'desert_cam'],

        'carrier': ['base',
                    'red', 'yellow', 'orange',
                    'green', 'dark_blue', 'light_blue',
                    'pink', 'violet', 'black',
                    'gold',
                    'pobeda',],

        'striker': ['base',
                    'red', 'yellow', 'orange',
                    'green', 'dark_blue', 'light_blue',
                    'pink', 'violet', 'black',
                    'gold'
                    ],

        'harrier': ['base',
                    'red', 'yellow', 'orange',
                    'green', 'dark_blue', 'light_blue',
                    'pink', 'violet', 'black',
                    'gold'
                    ],

        'demolisher': ['base',
                       'red', 'yellow', 'orange',
                       'green', 'dark_blue', 'light_blue',
                       'pink', 'violet', 'black',
                       'gold'
                       ],

        'observer': ['base',
                     'red', 'yellow', 'orange',
                     'green', 'dark_blue', 'light_blue',
                     'pink', 'violet', 'black',
                     'gold'
                     ],

        'sprinter': ['base',
                     'red', 'yellow', 'orange',
                     'green', 'dark_blue', 'light_blue',
                     'pink', 'violet', 'black',
                     'gold'
                     ],

        'hammer': ['base',
                     'red', 'yellow', 'orange',
                     'green', 'dark_blue', 'light_blue',
                     'pink', 'violet', 'black',
                     'gold'
                     ],

        'sailor': ['base',
                 ],
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
                        ('striker', 'Striker'),
                        ('demolisher', 'Demolisher'),
                        ('sprinter', 'Sprinter'),
                        ('harrier', 'Harrier'),
                        ('sailor', 'Sailor'),
                        ('hammer', 'Hammer'),
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

                        ('gold', 'золотой'),

                        ('dreamflight', 'Dreamflight'), # сходка МСК 2024
                        ('black_gold', 'чёрно-золотой'),

                        ('green_cam', 'зелёный камуфляж'),
                        ('green_white_cam', 'бело-зелёный камуфляж'),
                        ('blue_cam', 'синий камуфляж'),
                        ('desert_cam', 'песочный камуфляж'),
                        ('wood', 'дерево'),
                        ('airball', 'Airball'),
                        ('pobeda', 'пузырьки'),  # в стиле лоукостера
                    )

    plane = models.CharField(
        max_length=10,
        choices=planesChoices,
    )

    color = models.CharField(
        max_length=20,
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
