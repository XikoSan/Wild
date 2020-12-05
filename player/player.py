# coding=utf-8
import datetime
# import os
import pytz
import sys
from PIL import Image
# from datetime import timedelta
# from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from io import BytesIO

from region.region import Region


# from gamecore.all_models.Party.party import Party
# from gamecore.all_models.Party.position import PartyPosition
# from gamecore.all_models.gov.state import State
# from .region import Region


class Player(models.Model):
    # учетная запись игрока
    account = models.OneToOneField('auth.User', default='', on_delete=models.CASCADE, verbose_name='Учетная запись')
    # Показатель того, что игрок забанен
    banned = models.BooleanField(default=False, null=False, verbose_name='Бан')
    # последний использовавшийся ip
    user_ip = models.CharField(max_length=15, blank=True, verbose_name='IP пользователя')
    # никнейм игрока
    nickname = models.CharField(max_length=30, blank=False, verbose_name='Никнейм')
    # фото профиля игрока
    image = models.ImageField(upload_to='img/avatars/', blank=True, null=True, verbose_name='Аватар')
    # Часовые пояса на выбор игрока
    timeZoneChoices = [(tz, tz) for tz in pytz.common_timezones]
    # Часовой пояс игрока(самое длинное имя часового пояса 32 символа. Берем 50 с запасом)
    time_zone = models.CharField(max_length=50, default=timezone.get_default_timezone_name(),
                                 blank=False, choices=timeZoneChoices, verbose_name='Часовой пояс')

    # регион проживания
    region = models.ForeignKey(Region, default=None, null=True, on_delete=models.SET_NULL, blank=True,
                               verbose_name='Регион проживания', related_name="region")
    # регион прописки
    residency = models.ForeignKey(Region, default=None, null=True, on_delete=models.SET_NULL, blank=True,
                                  verbose_name='Прописка', related_name="residency")
    # время получения прописки
    residency_date = models.DateTimeField(default=timezone.now, blank=True, verbose_name='Дата получния прописки')

    # -----------партия----------------
    #
    # # партия игрока
    # party = models.ForeignKey(Party, default=None, null=True, on_delete=models.SET_NULL, blank=True,
    #                           verbose_name='Партия', related_name="party")
    # # позиция в партии
    # party_post = models.ForeignKey(PartyPosition, default=None, null=True, on_delete=models.SET_NULL, blank=True,
    #                                verbose_name='Должность в партии', related_name="party_post")

    # -----------опыт----------------

    # текущий уровень
    level = models.IntegerField(default=1, verbose_name='Уровень')
    # текущее число опыта
    exp = models.IntegerField(default=0, verbose_name='Опыт')

    # -----------энергия----------------

    # текущее значение энергии
    energy = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)],
                                 verbose_name='Энергии сейчас')
    # дата последнего пополнения
    last_refill = models.DateTimeField(default=datetime.datetime(2020, 10, 28, 0, 0), blank=True,
                                       verbose_name='Перезарядка будет доступна в')
    #
    # # дата последнего есстественного прироста
    # natural_refill = models.DateTimeField(default=None, null=True, blank=True, verbose_name='Время прироста')
    # # индекс во время последнего прироста
    # last_top = models.IntegerField(default=0, null=True, blank=True,
    #                                verbose_name='Рейтинг госпиталя при последнем приросте')

    # -----------навыки игрока----------------

    # # значение силы игрока
    # power = models.IntegerField(default=1)
    # # значение знаний игрока
    # knowlege = models.IntegerField(default=1)
    # # значение выносливости игрока
    # endurance = models.IntegerField(default=1)
    #
    # # флаг изучения в данный момент
    # # тип партии
    # choice_power = 'power'
    # choice_knowlege = 'knowlege'
    # choice_endurance = 'endurance'
    # skillChoices = (
    #     (choice_power, 'Сила'),
    #     (choice_knowlege, 'Знания'),
    #     (choice_endurance, 'Выносливость'),
    # )
    # learning = models.CharField(
    #     max_length=10,
    #     default=None,
    #     null=True,
    #     blank=True,
    #     choices=skillChoices
    # )
    # # время получение следующего уровня навыка (если изучается)
    # learning_up_date = models.DateTimeField(default=datetime.datetime(2020, 10, 28, 0, 0), blank=True)
    # # id фонового процесса (обучения)
    # task_id = models.CharField(max_length=150, blank=True, null=True, verbose_name='id фонового процесса')
    #
    # # значение навыка добычи ресурсов
    # mining_skill = models.IntegerField(default=1)

    # -----------склад ресурсов----------------

    # запасы денег
    cash = models.BigIntegerField(default=10000, verbose_name='Наличные')
    # ёмкость кошелька
    # cash_cap = models.BigIntegerField(default=10000, verbose_name='Ёмкость кошелька')
    # время завершения расширения Кошелька
    # expansion_end = models.DateTimeField(default=None, null=True, blank=True)

    # запасы золота
    gold = models.BigIntegerField(default=100, verbose_name='Золото')
    # запасы золота, которые будут выданы после релиза
    prize_gold = models.BigIntegerField(default=0, verbose_name='Релизное золото')
    # энергетик
    bottles = models.BigIntegerField(default=1000, verbose_name='Энергетики')

    # -----------перелёты----------------

    # регион назначения
    destination = models.ForeignKey(Region, default=None, null=True, on_delete=models.SET_NULL, blank=True,
                                    verbose_name='Регион назначения', related_name="destination")
    # # время вылета
    # departure = models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), blank=True)
    # время прилёта
    arrival = models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), blank=True)

    # рассчет естественного прироста с учётом уровня медицины в текущем регионе
    # def increase_calc(self):
    #     # если дата последнего прироста пуста (только зарегистрировался)
    #     if not self.natural_refill:
    #         # если энергии меньше ста
    #         if self.energy < 100:
    #             # пополняем
    #             if self.region.med_top == 5:
    #                 self.energy += 15
    #             elif self.region.med_top == 4:
    #                 self.energy += 13
    #             elif self.region.med_top == 3:
    #                 self.energy += 12
    #             elif self.region.med_top == 2:
    #                 self.energy += 11
    #             else:
    #                 self.energy += 10
    #             # запоминаем дату восстановления
    #             self.natural_refill = timezone.now()
    #             # запоминаем рейтинг медицины
    #             self.last_top = self.region.med_top
    #
    #     # инчае если с момента последнего пополнения прошло более десяти минут
    #     elif (timezone.now() - self.natural_refill).total_seconds() >= 600:
    #         # узнаем сколько раз по десять минут прошло
    #         counts = (timezone.now() - self.natural_refill).total_seconds() // 600
    #         # остаток от деления понадобится чтобы указать время обновления
    #         modulo = (timezone.now() - self.natural_refill).total_seconds() % 600
    #         # в зависимости от рейтинга
    #         if self.last_top == 5:
    #             # если интервалов больше шести (энергии станет заведомо больше ста)
    #             if counts > 6:
    #                 self.energy = 100
    #             else:
    #                 if self.energy + (15 * counts) >= 100:
    #                     self.energy = 100
    #                 else:
    #                     self.energy += 15 * counts
    #         elif self.last_top == 4:
    #             # если интервалов больше семи (энергии станет заведомо больше ста)
    #             if counts > 7:
    #                 self.energy = 100
    #             else:
    #                 if self.energy + (13 * counts) >= 100:
    #                     self.energy = 100
    #                 else:
    #                     self.energy += 13 * counts
    #         elif self.last_top == 3:
    #             # если интервалов больше семи (энергии станет заведомо больше ста)
    #             if counts > 8:
    #                 self.energy = 100
    #             else:
    #                 if self.energy + (12 * counts) >= 100:
    #                     self.energy = 100
    #                 else:
    #                     self.energy += 12 * counts
    #         elif self.last_top == 2:
    #             # если интервалов больше 9 (энергии станет заведомо больше ста)
    #             if counts > 9:
    #                 self.energy = 100
    #             else:
    #                 if self.energy + (11 * counts) >= 100:
    #                     self.energy = 100
    #                 else:
    #                     self.energy += 11 * counts
    #         else:
    #             # если интервалов больше 10 (энергии станет заведомо больше ста)
    #             if counts > 10:
    #                 self.energy = 100
    #             else:
    #                 if self.energy + (10 * counts) >= 100:
    #                     self.energy = 100
    #                 else:
    #                     self.energy += 10 * counts
    #
    #         # запоминаем дату восстановления
    #         self.natural_refill = timezone.now() - datetime.timedelta(seconds=modulo)
    #         # запоминаем рейтинг медицины
    #         self.last_top = self.region.med_top
    #
    #     self.save()

    # сохранение профиля с изменением размеров и названия картинки профиля
    def save(self):
        # если картинка есть (добавили или изменили)
        if (self.image):
            # Opening the uploaded image
            im = Image.open(self.image)

            output = BytesIO()

            # Resize/modify the image
            im = im.resize((300, 300))

            # after modifications, save it to the output
            im.save(output, format='PNG', quality=100)
            output.seek(0)

            # change the imagefield value to be the newley modifed image value
            self.image = InMemoryUploadedFile(output, 'ImageField',
                                              "%(account)s_%(player)s.png" % {"account": self.account.pk,
                                                                              "player": self.pk}, 'image/png',
                                              sys.getsizeof(output), None)

            super(Player, self).save()
        # если картинку удалили или её не было
        else:
            super(Player, self).save()

    def __str__(self):
        return self.nickname

    # Свойства класса
    class Meta:
        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"
