from django import forms

from .player import Player
from PIL import Image
from django import forms
from django.core.files import File


# модель отображения формы регистрации персонажа
class NewPlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ('nickname', 'image', 'time_zone')


class ImageForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Player
        fields = ('image', 'x', 'y', 'width', 'height',)

    # def save(self, player_pk):
    #     player = Player.objects.get(pk=player_pk)
    #     player = super(ImageForm, player).save()
    #
    #     x = self.cleaned_data.get('x')
    #     y = self.cleaned_data.get('y')
    #     w = self.cleaned_data.get('width')
    #     h = self.cleaned_data.get('height')
    #
    #     image = Image.open(player.image)
    #     cropped_image = image.crop((x, y, w + x, h + y))
    #     resized_image = cropped_image.resize((400, 400), Image.ANTIALIAS)
    #     resized_image.save(player.image.path)
    #
    #     return player

