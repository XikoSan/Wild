# coding=utf-8
import os
import shutil
from io import BytesIO

from PIL import Image
from django import forms
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from bill.models.bill import Bill
from state.models.parliament.deputy_mandate import DeputyMandate
from state.models.parliament.parliament import Parliament
from state.models.state import State


# Изменить герб государства
class ChangeCoat(Bill):
    # герб страны
    image = models.ImageField(upload_to='img/state_avatars/', blank=True, null=True, verbose_name='Герб')

    @staticmethod
    def new_bill(request, player, parliament):

        if ChangeCoat.objects.filter(running=True, initiator=player).exists():
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Ограничение: не более одного законопроекта данного типа',
            }

        form = ImageForm(request.POST, request.FILES)

        if not form.is_valid():
            return {
                'header': 'Новый законопроект',
                'grey_btn': 'Закрыть',
                'response': 'Ошибка формы нового герба',
            }

        # ура, все проверили
        bill = ChangeCoat(
            running=True,
            parliament=parliament,
            initiator=player,
            voting_start=timezone.now(),
        )

        setattr(bill, 'image', form.cleaned_data['image'])

        bill.save()

        x = form.cleaned_data['x']
        y = form.cleaned_data['y']
        w = form.cleaned_data['width']
        h = form.cleaned_data['height']

        image = Image.open(getattr(bill, 'image'))

        cropped_image = image.crop((x, y, w + x, h + y))
        resized_image = cropped_image.resize((400, 400), Image.ANTIALIAS)
        resized_image.save(getattr(bill, 'image').path)

        return {
            'response': 'ok',
        }

    # выполнить законопроект
    def do_bill(self):
        b_type = None
        state = State.objects.get(pk=self.parliament.state.pk)

        original = os.path.join(settings.MEDIA_ROOT, self.image.name)

        target = os.path.join(settings.MEDIA_ROOT,
                              'img/state_avatars/' + str(state.pk) + '.' + self.image.path.split('.')[1])

        shutil.copyfile(original, target)

        t_image = Image.open(target)

        thumb_io = BytesIO()
        t_image.save(thumb_io, t_image.format, quality=60)

        state.image.save(t_image.filename.split('/')[-1], ContentFile(thumb_io.getvalue()), save=False)
        state.save()

        b_type = 'ac'
        ChangeCoat.objects.filter(pk=self.pk).update(type=b_type, running=False, voting_end=timezone.now())

        for bill in ChangeCoat.objects.filter(parliament=self.parliament, image__isnull=False).exclude(
                pk=self.pk).exclude(running=True):
            bill.image.delete(save=True)

    @staticmethod
    def get_draft(state):
        data = {'form': ImageForm()}

        return data, 'state/redesign/drafts/change_coat.html'

    @staticmethod
    def get_new_draft(state):
        data = {
            'form': ImageForm(),
            'state': state
        }

        return data, 'state/redesign/drafts/change_coat.html'

    def get_bill(self, player, minister, president):

        has_right = False
        if minister:
            for right in minister.rights.all():
                if self.__class__.__name__ == right.right:
                    has_right = True
                    break

        data = {
            'bill': self,
            'title': self._meta.verbose_name_raw,
            'player': player,
            'president': president,
            'has_right': has_right,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/gov/bills/change_coat.html'

    def get_new_bill(self, player, minister, president):

        has_right = False
        if minister:
            for right in minister.rights.all():
                if self.__class__.__name__ == right.right:
                    has_right = True
                    break

        data = {
            'bill': self,
            'title': self._meta.verbose_name_raw,
            'player': player,
            'president': president,
            'has_right': has_right,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/redesign/bills/change_coat.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):
        data = {'bill': self, 'title': self._meta.verbose_name_raw, 'player': player}

        return data, 'state/gov/reviewed/change_coat.html'


    # получить шаблон рассмотренного законопроекта
    def get_new_reviewed_bill(self, player):
        data = {'bill': self, 'title': self._meta.verbose_name_raw, 'player': player}

        return data, 'state/redesign/reviewed/change_coat.html'


    def __str__(self):
        return self.parliament.state.title

    # Свойства класса
    class Meta:

        verbose_name = "Новый герб государства"
        verbose_name_plural = "Смена гербов государств"


# сигнал прослушивающий создание законопроекта, после этого формирующий таску
@receiver(post_save, sender=ChangeCoat)
def save_post(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()


# сигнал удаляющий таску
@receiver(post_delete, sender=ChangeCoat)
def delete_post(sender, instance, using, **kwargs):
    if instance.task:
        instance.task.delete()


class ImageForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = ChangeCoat
        fields = ('image', 'x', 'y', 'width', 'height',)

