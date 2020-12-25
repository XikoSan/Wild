import datetime
from django.db import models

# from PIL import Image
# from io import BytesIO
# from django.core.files.uploadedfile import InMemoryUploadedFile
# import sys
# import gamecore.all_models.region as rgn
from region.region import Region


# Create your models here.

class Party(models.Model):
    # название партии
    title = models.CharField(max_length=30, verbose_name='Название партии')
    # тип партии
    open = 'op'
    private = 'pt'
    partyTypeChoices = (
        (open, 'Открытая'),
        (private, 'Частная'),
    )
    type = models.CharField(
        max_length=2,
        choices=partyTypeChoices,
        default=open,
    )

    # время основания партии
    foundation_date = models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), blank=True)
    # описание партии
    description = models.CharField(max_length=300, blank=True, null=True, verbose_name='Описание партии')
    # картинка партии
    image = models.ImageField(upload_to='img/party_avatars/', blank=True, null=True, verbose_name='Герб партии')
    # картинка партийного фона
    members_image_link = models.CharField(max_length=150, blank=True, null=True,
                                          verbose_name='Ссылка партийный фон')
    # регион партии
    region = models.ForeignKey(Region, default=None, null=True, on_delete=models.SET_NULL, blank=True,
                               verbose_name='Регион размещения', related_name="party_region")

    # удалено
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    # # id фонового процесса (начала или конца праймериз)
    # task_id = models.CharField(max_length=150, blank=True, null=True, verbose_name='id фонового процесса')

    def __str__(self):
        return self.title

    # Свойства класса
    class Meta:
        verbose_name = "Партия"
        verbose_name_plural = "Партии"
