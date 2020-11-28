from django import forms

from .player import Player


# модель отображения формы регистрации персонажа
class NewPlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ('nickname', 'image', 'time_zone')