# coding=utf-8
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy, pgettext_lazy
from datetime import datetime, timedelta
from player.logs.log import Log


# запись об передаче денег
class CashLog(Log):
    # денег передано или получено
    cash = models.BigIntegerField(default=0, verbose_name='Денег передано')
    # произвольный объект активности, в связи с которой были переданы или получены деньги
    content_type = models.ForeignKey(ContentType, blank=True, null=True, on_delete=models.SET_NULL)
    object_id = models.PositiveIntegerField(blank=True, null=True)

    activity = GenericForeignKey('content_type', 'object_id')
    # текст активности
    activityChoices = (
        ('daily',  pgettext_lazy('cash_log', 'Финансирование')),
        ('mine',  pgettext_lazy('cash_log', 'Майнинг')),
        ('flyin', pgettext_lazy('cash_log', 'Перелёт')),
        ('n_str', pgettext_lazy('cash_log', 'Новый Склад')),
        ('store', pgettext_lazy('cash_log', 'Операции со Складом')),
        ('trans', pgettext_lazy('cash_log', 'Передача товаров')),
        ('trade', pgettext_lazy('cash_log', 'Торговля')),
        ('bonus', 'Бонус-код'),
        ('auct', pgettext_lazy('cash_log', 'Гос. закупки')),
        ('skill', pgettext_lazy('cash_log', 'Навыки')),
        ('box', pgettext_lazy('cash_log', 'Лутбокс')),
        ('buy_box', pgettext_lazy('cash_log', 'Покупка лутбокса')),

        # обучение
        ('financing', 'Награда за получение Финансирования'),
        # обучение
        ('edu_skill', 'обучение: Изучение характеристики'),
    )
    activity_txt = models.CharField(
        max_length=10,
        choices=activityChoices,
        blank=True,
        null=True
    )

    @staticmethod
    def create(player, cash, activity_txt):
        cash_log = CashLog(player=player, cash=cash, activity_txt=activity_txt)
        cash_log.save()

        interval = datetime.now() - timedelta(days=30)
        CashLog.objects.filter(player=player, dtime__lt=interval).delete()


    def __str__(self):
        return str(self.cash) + ' за ' + str(self.get_activity_txt_display())

    # Свойства класса
    class Meta:
        verbose_name = "Лог передачи денег"
        verbose_name_plural = "Логи передачи денег"
