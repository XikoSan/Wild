# coding=utf-8
from django.apps import apps
from django.db import models

from storage.models.good import Good


# Чертёж (схема производства) товара
class Blueprint(models.Model):
    # название чертежа
    name = models.CharField(max_length=50,
                            default=None, null=True, blank=True,
                            verbose_name='Название')

    # товар для производства
    good = models.ForeignKey(Good, on_delete=models.CASCADE, verbose_name='Продукция')

    # требуемое количество энергии
    energy_cost = models.IntegerField(default=1, verbose_name='Затраты энергии')

    # требуемое количество Наличных
    cash_cost = models.IntegerField(default=1, verbose_name='Затраты Наличных')

    def __str__(self):
        Component = apps.get_model('factory.Component')

        ret = None
        if self.name:
            ret = self.name

        elif Component.objects.filter(blueprint=self).exists():
            for comp in Component.objects.filter(blueprint=self):
                if not ret:
                    ret = f'{comp.count} {comp.good.name}'
                else:
                    ret += f', {comp.count} {comp.good.name}'

        else:
            ret += f'{self.good.name} {self.pk}'

        return ret

    # Свойства класса
    class Meta:
        verbose_name = "Чертёж"
        verbose_name_plural = "Чертежи"
