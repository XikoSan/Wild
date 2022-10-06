# coding=utf-8
from django.db import models
from django.conf import settings
from player.player import Player

# Настройки игрока
class PlayerSettings(models.Model):
    # персонаж игрока
    player = models.ForeignKey(Player, default=None, on_delete=models.CASCADE, verbose_name='Игрок',
                               related_name="character_id")

    color_back = models.CharField(
        max_length=6,
        default='28353E',
    )

    color_block = models.CharField(
        max_length=6,
        default='284E64',
    )

    color_text = models.CharField(
        max_length=6,
        default='FFFFFF',
    )

    color_acct = models.CharField(
        max_length=6,
        default='EB9929',
    )

    # язык по умолчанию
    language = models.CharField(max_length=7, default=None, blank=True, null=True, choices=settings.LANGUAGES, verbose_name='Язык в игре')

    # # Показатель того, что игрок отображает раздел гайдов
    # guides_button = models.BooleanField(default=True, blank=False, null=False, verbose_name='Гайды')
    #
    # Показатель того, что игрок использует партийный аватар
    party_back = models.BooleanField(default=True, blank=False, null=False, verbose_name='Партийный фон')

    # # показатель того, что игрок по умолчанию оплачивает доставку войск в соседние регионы
    # delivery_pay = models.BooleanField(default=False, blank=False, null=False, verbose_name='Оплачивает доставку войск')
    #
    # # тип карты
    # as_pic = 'pict'
    # as_list = 'list'
    # mapTypeChoices = (
    #     (as_pic, 'Изображение'),
    #     (as_list, 'Список'),
    # )
    # map_type = models.CharField(
    #     max_length=4,
    #     choices=mapTypeChoices,
    #     default=as_pic,
    # )
    #
    # # разрешение на пожертвования
    # donate_all = 'all'
    # donate_party = 'party'
    # donate_nobody = 'nobody'
    # donateTypeChoices = (
    #     (donate_all, 'Все'),
    #     (donate_party, 'Партия'),
    #     (donate_nobody, 'Никто'),
    # )
    # donate_type = models.CharField(
    #     max_length=6,
    #     choices=donateTypeChoices,
    #     default=donate_all,
    # )
    #
    # # разрешение на просмотр региона нахождения
    # location_all = 'all'
    # location_party = 'party'
    # location_nobody = 'nobody'
    # locationTypeChoices = (
    #     (location_all, 'Все'),
    #     (location_party, 'Партия'),
    #     (location_nobody, 'Никто'),
    # )
    # location_type = models.CharField(
    #     max_length=6,
    #     choices=locationTypeChoices,
    #     default=location_all,
    # )

    def __str__(self):
        return self.player.nickname

    # Свойства класса
    class Meta:
        verbose_name = "Настройки игрока"
        verbose_name_plural = "Настройки игрока"