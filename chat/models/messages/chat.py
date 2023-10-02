from django.db import models

# чат. Ничего не содержит, просто нужен для того, чтобы на него ссылались, как на уникальный ID конфы
class Chat(models.Model):

    def __str__(self):
        return str(f'Чат {self.pk}')

    # Свойства класса
    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"
