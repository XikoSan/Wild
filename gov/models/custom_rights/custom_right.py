from django.db import models


# кастомные права министров
class CustomRight(models.Model):
    abstract = True

    # получить шаблон прав министра
    @staticmethod
    def get_form(state):
        return

    # Свойства класса
    class Meta:
        abstract = True
