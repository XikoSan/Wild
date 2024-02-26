from django.db import models
from player.player import Player

# статья (авторская)
class Article(models.Model):

    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name='Автор')

    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    # заголовок статьи
    title = models.CharField(max_length=100, verbose_name='Статья')

    # текст статьи
    body = models.TextField(verbose_name='Статья')

    # показывать в закрепленных
    pinned = models.BooleanField(default=False, verbose_name='Закреплено')

    # приоритет закрепления ( 0 - самый большой )
    pin_order = models.IntegerField(default=0, verbose_name='Приоритет закрепления')

    def __str__(self):
        return self.player.nickname + ' ' + str(self.date.strftime('%Y-%m-%d %H:%M'))

    # Свойства класса
    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
