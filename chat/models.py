from django.contrib.auth import get_user_model
from django.db import models
from player.player import Player

class Message(models.Model):
    author = models.ForeignKey(
        Player, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.nickname + ': ' + str(self.content[:20])


class Chat(models.Model):
    chat_id = models.CharField(max_length=10, blank=False, verbose_name='Код чата')

    messages = models.ManyToManyField(Message, blank=True, verbose_name='сообщения')

    def __str__(self):
        return "{}".format(self.chat_id, )


# class ChatOnline(models.Model):
#     player = models.ForeignKey(
#         Player, on_delete=models.CASCADE)
#     online = models.IntegerField(default=0, verbose_name='Онлайн (число чатов)')
#
#     def __str__(self):
#         return self.player.nickname + ' в ' + str(self.online) + ' чатах'
