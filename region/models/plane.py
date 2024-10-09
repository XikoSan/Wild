# coding=utf-8
from django import forms
from django.apps import apps
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy, pgettext_lazy, ugettext as _

from player.player import Player


# Владелец самолёта
class Plane(models.Model):
    # Показатель того, что игрок использует
    in_use = models.BooleanField(default=False, null=False, verbose_name='Используется')

    # владелец склада
    player = models.ForeignKey(Player, default=None, null=True, on_delete=models.CASCADE, verbose_name='Владелец')

    # кастомное имя самолета
    nickname = models.CharField(max_length=25, blank=True, default='', verbose_name='Никнейм')

    # бортовой номер
    number = models.IntegerField(default=0, verbose_name='Бортовой номер')

    planes = {

        'nagger': ['base', 'black_gold', 'dreamflight'],

        'beluzzo': ['base'],

        'pretender': ['base',
                      'red', 'yellow', 'orange',
                      'green', 'dark_blue', 'light_blue',
                      'pink', 'violet', 'black',
                      'wood', 'gold'
                      ],

        'trickster': ['base',
                      'red', 'yellow', 'orange',
                      'green', 'dark_blue', 'light_blue',
                      'pink', 'violet', 'black',
                      'corny', 'redline',
                      'gold'
                      ],

        'smuggler': ['base',
                     'red', 'yellow', 'orange',
                     'green', 'dark_blue', 'light_blue',
                     'pink', 'violet', 'black',
                     'green_cam', 'blue_cam', 'desert_cam',
                     'gold'
                     ],

        'chaser': ['base',
                   'black'
                   ],

        'reaper': ['base',
                   'red', 'yellow', 'orange',
                   'green', 'dark_blue', 'light_blue',
                   'pink', 'violet', 'black',
                   'airball',
                   'green_cam', 'blue_cam', 'desert_cam',
                   'gold'],

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
                    'pobeda', ],

        'striker': ['base',
                    'red', 'yellow', 'orange',
                    'green', 'dark_blue', 'light_blue',
                    'pink', 'violet', 'black',
                    'green_white_cam',
                    'green_cam', 'blue_cam', 'desert_cam',
                    'gold'
                    ],

        'harrier': ['base',
                    'red', 'yellow', 'orange',
                    'green', 'dark_blue', 'light_blue',
                    'pink', 'violet', 'black',
                    'green_cam', 'blue_cam', 'desert_cam',
                    'gold'
                    ],

        'demolisher': ['base',
                       'red', 'yellow', 'orange',
                       'green', 'dark_blue', 'light_blue',
                       'pink', 'violet', 'black',
                       'standard', 'hexagon', 'white_cam',
                       'gold'
                       ],

        'observer': ['base',
                     'red', 'yellow', 'orange',
                     'green', 'dark_blue', 'light_blue',
                     'pink', 'violet', 'black', 'pobeda',
                     'gold', 'black_gold'
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
                   'green_cam', 'blue_cam', 'desert_cam',
                   'gold'
                   ],

        'sailor': ['base', 'android',
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
        ('beluzzo', 'Диск Белуццо'),
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
        ('black_gold', 'чёрно-золотой'),
        ('wood', 'дерево'),

        ('dreamflight', 'Dreamflight'),  # сходка МСК 2024
        ('android', 'Android tester'),  # тест андроида осенью 2024

        ('hexagon', 'гексагон'),
        ('standard', 'стандартная схема'),
        ('green_cam', 'зелёный камуфляж'),
        ('white_cam', 'белый камуфляж'),
        ('green_white_cam', 'бело-зелёный камуфляж'),
        ('blue_cam', 'синий камуфляж'),
        ('desert_cam', 'песочный камуфляж'),
        ('corny', 'царь полей'),
        ('redline', 'красная линия'),
        ('airball', 'Airball'),
        ('pobeda', 'пузырьки'),  # в стиле лоукостера
    )

    plane = models.CharField(
        max_length=10,
        choices=planesChoices,
    )

    common_colors = [
        'base',
        'red', 'yellow', 'orange',
        'green', 'dark_blue', 'light_blue',
        'violet',
    ]

    rare_colors = [
        'black', 'pink', 'green_white_cam', 'green_cam', 'blue_cam', 'desert_cam', 'pobeda', 'airball',
        'corny', 'redline', 'standard', 'hexagon', 'white_cam', 'android',
    ]

    gold_colors = ['gold', 'black_gold', 'wood']

    color = models.CharField(
        max_length=20,
        choices=colorChoices,
    )

    def image_tag(self):
        if self.plane:
            return mark_safe(
                f'<img src="/static/img/planes/{self.plane}/{self.plane}_{self.color}.svg" width="150" height="150" />')
        else:
            return mark_safe(f'<img src="/static/img/planes/nagger/nagger_base.svg" width="150" height="150" />')

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


# сигнал прослушивающий создание
@receiver(post_save, sender=Plane)
def save_post(sender, instance, created, **kwargs):
    if created:
        if instance.color in Plane.gold_colors:
            last_number = Plane.objects.only('pk').filter(color__in=Plane.gold_colors).order_by(
                '-number').first().number
            instance.number = last_number + 1

            instance.save()

    if instance.in_use:
        Plane.objects.filter(player=instance.player).exclude(pk=instance.pk).update(in_use=False)
