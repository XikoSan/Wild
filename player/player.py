# coding=utf-8
import datetime
import pytz
from django.apps import apps
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.timezone import make_aware
from django.utils.translation import pgettext
from django_celery_beat.models import PeriodicTask

from party.party import Party
from party.position import PartyPosition
from player.views.set_cah_log import set_cash_log
from region.building.hospital import Hospital
from region.region import Region
from state.models.state import State
from wild_politics.settings import JResponse


class Player(models.Model):
    # учетная запись игрока
    account = models.OneToOneField('auth.User', default='', on_delete=models.CASCADE, verbose_name='Учетная запись')
    # Показатель того, что игрок забанен
    banned = models.BooleanField(default=False, null=False, verbose_name='Бан')
    # Показатель того, что игрок забанен в чате
    chat_ban = models.BooleanField(default=False, null=False, verbose_name='Бан чата')
    # последний использовавшийся ip
    user_ip = models.CharField(max_length=50, blank=True, verbose_name='IP пользователя')
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

    # о себе
    bio = models.TextField(max_length=250, default='', null=True, blank=True, verbose_name='Биография')

    # -----------партия----------------

    # партия игрока
    party = models.ForeignKey(Party, default=None, null=True, on_delete=models.SET_NULL, blank=True,
                              verbose_name='Партия', related_name="party")
    # позиция в партии
    party_post = models.ForeignKey(PartyPosition, default=None, null=True, on_delete=models.SET_NULL, blank=True,
                                   verbose_name='Должность в партии', related_name="party_post")

    # -----------опыт----------------

    # текущий уровень
    level = models.IntegerField(default=1, verbose_name='Уровень')
    # текущее число опыта
    exp = models.IntegerField(default=0, verbose_name='Опыт')

    # -----------энергия----------------

    # текущее значение энергии
    energy = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)],
                                 verbose_name='Энергии сейчас')
    # дата ближайшего возможного пополнения
    last_refill = models.DateTimeField(default=datetime.datetime(2020, 10, 28, 0, 0), blank=True,
                                       verbose_name='Перезарядка будет доступна в')

    # дата последнего есстественного прироста
    natural_refill = models.DateTimeField(default=None, null=True, blank=True, verbose_name='Время прироста')
    # индекс во время последнего прироста
    last_top = models.IntegerField(default=0, null=True, blank=True,
                                   verbose_name='Рейтинг госпиталя при последнем приросте')

    # -----------дневной квест на трату энергии----------------
    # количество энергии, которую надо тратить ежедневно
    energy_limit = 3000
    # расход энергии за эти сутки (еще не оплаченный)
    energy_consumption = models.IntegerField(default=0, verbose_name='Расход энергии')
    # расход энергии, за который игрок уже забрал деньги
    paid_consumption = models.IntegerField(default=0, verbose_name='Оплаченный расход энергии')
    # сумма, которую игрок уже забрал
    paid_sum = models.IntegerField(default=0, verbose_name='Оплачено сегодня')
    # Показатель того, что прогрессия на сегодня завершена
    daily_fin = models.BooleanField(default=False, null=False, verbose_name='Дейлик пройден')

    # -----------навыки игрока----------------

    # значение силы игрока
    power = models.IntegerField(default=1)
    # значение знаний игрока
    knowledge = models.IntegerField(default=1)
    # значение выносливости игрока
    endurance = models.IntegerField(default=1)

    # -----------склад ресурсов----------------

    # дата истечения премиум-акккаунта
    premium = models.DateTimeField(default=timezone.now, blank=True,
                                   verbose_name='Премиум, до')

    # количество премиум-карточек Wild Pass
    cards_count = models.IntegerField(default=0, verbose_name='Премиум-карты')

    # -----------склад ресурсов----------------

    # запасы денег
    cash = models.BigIntegerField(default=10000, verbose_name='Наличные')
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
    # таска полета
    task = models.OneToOneField(PeriodicTask, on_delete=models.SET_NULL, null=True, blank=True)
    # время прилёта
    arrival = models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), blank=True)

    def energy_cons(self, value, mul=1):
        self.energy_consumption += value * mul
        self.energy -= value
        self.save()

        PlayerRegionalExpense = apps.get_model('player.PlayerRegionalExpense')

        if PlayerRegionalExpense.objects.filter(player=self, region=self.region).exists():
            reg_exp = PlayerRegionalExpense.objects.get(player=self, region=self.region)
            reg_exp.energy_consumption += value * mul

        else:
            reg_exp = PlayerRegionalExpense(
                player=self,
                region=self.region,
                energy_consumption=value * mul
            )

        reg_exp.save()

        GameEvent = apps.get_model('player.GameEvent')
        EventPart = apps.get_model('player.EventPart')
        GlobalPart = apps.get_model('player.GlobalPart')

        if GameEvent.objects.filter(running=True, event_start__lt=timezone.now(),
                                    event_end__gt=timezone.now()).exists():

            event_part = None

            if EventPart.objects.filter(
                    player=self,
                    event=GameEvent.objects.get(running=True, event_start__lt=timezone.now(),
                                                event_end__gt=timezone.now())
            ).exists():

                event_part = EventPart.objects.get(
                    player=self,
                    event=GameEvent.objects.get(running=True, event_start__lt=timezone.now(),
                                                event_end__gt=timezone.now())
                )
                event_part.points += value
                event_part.prize_check()
                event_part.save()

            else:
                event_part = EventPart(
                    player=self,
                    event=GameEvent.objects.get(running=True, event_start__lt=timezone.now(),
                                                event_end__gt=timezone.now()),
                    points=value
                )
                event_part.prize_check()
                event_part.save()

    #       ---- общий счет ----
            if GlobalPart.objects.filter(
                    event=GameEvent.objects.get(running=True, event_start__lt=timezone.now(),
                                                event_end__gt=timezone.now())
            ).exists():

                global_part = GlobalPart.objects.get(
                    event=GameEvent.objects.get(running=True, event_start__lt=timezone.now(),
                                                event_end__gt=timezone.now())
                )
                global_part.points += value
                event_part = global_part.prize_check(event_part)
                event_part.save()
                global_part.save()

            else:
                global_part = GlobalPart(
                    event=GameEvent.objects.get(running=True, event_start__lt=timezone.now(),
                                                event_end__gt=timezone.now()),
                    points=value
                )
                event_part = global_part.prize_check(event_part)
                event_part.save()
                global_part.save()

    # получить актуализированного Игрока
    @staticmethod
    @transaction.atomic
    def get_instance(**params):

        player = None
        # получаем запрошенную инстанцию Склада
        if Player.objects.filter(**params).exists():
            player = Player.objects.select_for_update().get(**params)
        else:
            return player

        player.increase_calc()

        SkillTraining = apps.get_model('player.SkillTraining')

        if SkillTraining.objects.filter(player=player).exists():
            skills = SkillTraining.objects.filter(player=player).order_by('end_dtime')

            for skill in skills:
                if skill.end_dtime <= timezone.now():

                    if skill.skill in ['power', 'knowledge', 'endurance']:
                        setattr(player, skill.skill, getattr(player, skill.skill) + 1)

                    else:
                        skill_cl = apps.get_model('skill.' + skill.skill)
                        if skill_cl.objects.filter(player=player).exists():
                            perk = skill_cl.objects.get(player=player)
                            perk.level += 1
                            perk.save()

                        else:
                            perk = skill_cl(
                                player=player,
                                level=1
                            )
                            perk.save()

                    # навык изучен, удаляем запись
                    skill.delete()

                else:
                    break

            player.save()

        return player

    # сбор денег из дейлика
    def daily_claim(self):

        power = self.power
        if power > 100:
            power = 100

        knowledge = self.knowledge
        if knowledge > 100:
            knowledge = 100

        endurance = self.endurance
        if endurance > 100:
            endurance = 100

        daily_limit = 15000 + (power * 100) + (knowledge * 100) + (endurance * 100)

        if self.destination:
            data = {
                'response': pgettext('mining', 'Дождитесь конца полёта'),
                'header': pgettext('mining', 'Ошибка получения финансирования'),
                'grey_btn': pgettext('mining', 'Закрыть'),
            }
            # return JResponse(data)
            return JResponse(data), 0
            # return HttpResponse('Дождитесь конца полёта')

        # energy_limit - количество энергии, которую надо выфармить за день
        if self.paid_consumption >= self.energy_limit:
            daily_procent = 100
        else:
            daily_procent = self.energy_consumption / ((self.energy_limit - self.paid_consumption) / 100)

        if daily_procent > 100:
            daily_procent = 100

        if self.paid_sum > daily_limit:
            daily_procent = 0

        if daily_procent == 0 or (self.paid_consumption >= self.energy_limit and daily_limit - self.paid_sum == 0):
            data = {
                'response': pgettext('mining', 'Нечего забирать'),
                'header': pgettext('mining', 'Ошибка получения финансирования'),
                'grey_btn': pgettext('mining', 'Закрыть'),
            }
            # return JResponse(data)
            return JResponse(data), 0

        # сумма, которую уже можно забрать
        count = int((daily_limit - self.paid_sum) / 100 * daily_procent)

        if count < 0:
            count = 0

        # бонус по выходным
        is_weekend = False
        if timezone.now().date().weekday() == 5 or timezone.now().date().weekday() == 6:
            if count != 0:
                is_weekend = True
                count += count

        taxed_count = 0
        PlayerRegionalExpense = apps.get_model('player.PlayerRegionalExpense')

        for expense in PlayerRegionalExpense.objects.filter(player=self):
            taxed_count += expense.get_taxes(count)

        PlayerRegionalExpense.objects.filter(player=self).delete()

        # # если дейлик ещё не закрывался сегодня
        # if not self.daily_fin:
        #     Finance = apps.get_model('skill.Finance')
        #     if Finance.objects.filter(player=self, level__gt=0).exists():
        #         if count != 0 and daily_procent == 100:
        #             taxed_count += daily_limit

        # отмечаем, что  дейлик закрыт:
        # если игрок прокачат навык, то не получит золотой бонус или Подпольное Финансирование
        if daily_procent == 100:
            self.daily_fin = True

        # выдаем деньги
        self.cash += taxed_count
        # прибавляем деньги ДО НАЛОГОВ к уже выплаченным
        if is_weekend:
            count = count / 2
        self.paid_sum += count
        # добавляем потраченную энергию к оплаченной
        self.paid_consumption += self.energy_consumption
        # занулем потраченное
        self.energy_consumption = 0

        self.save()

        return False, taxed_count

    # расчет естественного прироста с учётом уровня медицины в текущем регионе
    # прирост медки используется в mining.py
    def increase_calc(self):
        # нужно очистить дейлик
        if self.natural_refill \
                and timezone.now().date() > self.natural_refill.date():
            err, sum = self.daily_claim()
            if not err:
                # вынес потому что вызывает круговой импорт
                set_cash_log(self, sum, 'daily', self.natural_refill)
            self.energy_consumption = self.paid_consumption = self.paid_sum = 0
            self.daily_fin = False

        med_top = 1

        if Hospital.objects.filter(region=self.region).exists():
            # med_top = Hospital.objects.get(region=self.region).get_top()
            med_top = Hospital.objects.get(region=self.region).top

        # если дата последнего прироста пуста (только зарегистрировался)
        if not self.natural_refill:
            # если энергии меньше ста
            if self.energy < 100:
                # пополняем
                self.energy += Hospital.indexes[med_top]

                # запоминаем дату восстановления
                self.natural_refill = timezone.now()
                # запоминаем рейтинг медицины
                self.last_top = med_top

        # инчае если с момента последнего пополнения прошло более десяти минут
        elif (timezone.now() - self.natural_refill).total_seconds() >= 600:
            # узнаем сколько раз по десять минут прошло
            counts = int((timezone.now() - self.natural_refill).total_seconds() // 600)
            # остаток от деления понадобится чтобы указать время обновления
            modulo = (timezone.now() - self.natural_refill).total_seconds() % 600

            # считаем, сколько энергии станет при последнем индексе
            energy_sum = Hospital.indexes[self.last_top] * counts

            # если энергии заведомо больше ста
            if energy_sum > 100:
                self.energy = 100
            # если энергии с тем, что было игрока, больше ста
            elif self.energy + energy_sum > 100:
                self.energy = 100
            else:
                self.energy += energy_sum

            # запоминаем дату восстановления
            self.natural_refill = timezone.now() - datetime.timedelta(seconds=modulo)
            # запоминаем рейтинг медицины
            self.last_top = med_top

        self.save()

    def __str__(self):
        return self.nickname

    # Свойства класса
    class Meta:
        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"
