# coding=utf-8
import os

from PIL import Image
from django import forms
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from state.models.bills.bill import Bill
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
        resized_image = cropped_image.resize((250, 250), Image.ANTIALIAS)
        resized_image.save(getattr(bill, 'image').path)

        return {
            'response': 'ok',
        }

    # выполнить законопроект
    def do_bill(self):
        b_type = None
        state = State.objects.get(pk=self.parliament.state.pk)

        image = ContentFile(self.image.url)

        # image = Image.open(getattr(self, 'image'))

        state.image = self.image
        state.save()

        b_type = 'ac'
        ChangeCoat.objects.filter(pk=self.pk).update(type=b_type, running=False, voting_end=timezone.now())
        # ChangeCoat.objects.exclude(pk=self.pk, type__isnull=True).image.delete(save=True)

    @staticmethod
    def get_draft(state):
        data = {'form': ImageForm()}

        return data, 'state/gov/drafts/change_coat.html'

    def get_bill(self, player):

        data = {
            'bill': self,
            'title': self._meta.verbose_name_raw,
            'player': player,
            # проверяем, депутат ли этого парла игрок или нет
            'is_deputy': DeputyMandate.objects.filter(player=player, parliament=Parliament.objects.get(
                state=player.region.state)).exists(),
        }

        return data, 'state/gov/bills/change_coat.html'

    # получить шаблон рассмотренного законопроекта
    def get_reviewed_bill(self, player):
        data = {'bill': self, 'title': self._meta.verbose_name_raw, 'player': player}

        return data, 'state/gov/reviewed/change_coat.html'

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


class ImageForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = ChangeCoat
        fields = ('image', 'x', 'y', 'width', 'height',)
