from django.db import models


# кастомные права министров
class CustomRight(models.Model):
    abstract = True

    # получить шаблон прав министра
    @staticmethod
    def get_form(state):
        return

    # получить шаблон прав министра
    @staticmethod
    def get_new_form(state):
        return None, None

    # Свойства класса
    class Meta:
        abstract = True
