# coding=utf-8
import sys
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from io import BytesIO


class State(models.Model):
    # название страны
    title = models.CharField(max_length=255, verbose_name='Название государства')
    # герб страны
    image = models.ImageField(upload_to='img/state_avatars/', blank=True, null=True, verbose_name='Герб')
    # цвет на карте
    color = models.CharField(max_length=6, default="008542", verbose_name='Цвет государства')
    # время основания партии
    foundation_date = models.DateTimeField(default=None, blank=True, null=True)
    # тип государства
    stateTypeChoices = (
        ('parl', 'Парламентская республика'),
        ('pres', 'Президентская республика'),
    )
    type = models.CharField(
        max_length=4,
        choices=stateTypeChoices,
        default='parl',
    )

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    # id фонового процесса (начала или конца праймериз)
    # task_id = models.CharField(max_length=150, blank=True, null=True, verbose_name='id фонового процесса')

    # сохранение государства с изменением размеров и названия картинки профиля
    def save(self):
        # если картинка есть (добавили или изменили)
        if self.image:
            # Opening the uploaded image
            im = Image.open(self.image)

            output = BytesIO()

            # Resize/modify the image
            im = im.resize((300, 300))

            # after modifications, save it to the output
            im.save(output, format='PNG', quality=100)
            output.seek(0)

            # change the imagefield value to be the newley modifed image value
            self.image = InMemoryUploadedFile(output, 'ImageField', "%(state)s.png" % {"state": self.title},
                                              'image/png',
                                              sys.getsizeof(output), None)

            super(State, self).save()
        # если картинку удалили или её не было
        else:
            super(State, self).save()

    def __str__(self):
        return self.title

    # Свойства класса
    class Meta:
        verbose_name = "Государство"
        verbose_name_plural = "Государства"
