from django import forms

from party.party import Party


# модель отображения формы создания партии
class NewPartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ('title', 'description', 'image')
