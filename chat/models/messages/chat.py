from django.db import models
from state.models.state import State

# чат. Ничего не содержит, просто нужен для того, чтобы на него ссылались, как на уникальный ID конфы
class Chat(models.Model):

    # государство принадлежности
    state = models.ForeignKey(State, default=None, null=True, blank=True, on_delete=models.CASCADE, verbose_name='Государство', related_name="chat_state")

    def __str__(self):
        return str(f'Чат {self.pk}')

    # Свойства класса
    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"
