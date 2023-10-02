from django.db import models
from chat.models.messages.chat import Chat

# чат за сутки, либо последние 100 сообщений
class MessageBlock(models.Model):

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)

    date = models.DateTimeField(auto_now_add=True)

    messages = models.TextField()

    def __str__(self):
        return str(f'Сообщения {self.chat.pk} по {self.date.__str__()}')

    # Свойства класса
    class Meta:
        verbose_name = "Блок сообщений"
        verbose_name_plural = "Блоки сообщений"
