from django.db import models
from chat.models.messages.chat import Chat
from player.player import Player

# участники чата
class ChatMembers(models.Model):

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)

    player = models.ForeignKey(Player, on_delete=models.CASCADE)


    def __str__(self):
        return str(f'{self.player.pk} в чате {self.chat.pk}')

    # Свойства класса
    class Meta:
        verbose_name = "Участник чата"
        verbose_name_plural = "Участники чата"
