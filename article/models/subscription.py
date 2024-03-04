from django.db import models
from player.player import Player
from django.utils import timezone

# подписка на автора
class Subscription(models.Model):

    # подписчик
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name='Подписчик')

    # дата подписки
    date = models.DateTimeField(default=timezone.now, verbose_name='Дата подписки')

    # автор
    author = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name='Автор', related_name='author')


    def __str__(self):
        return self.player.nickname + ' подписан на ' + self.author.nickname

    # Свойства класса
    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
