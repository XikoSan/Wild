from django import forms

from party.party import Party


# модель отображения формы создания партии
class NewPartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ('title', 'description', 'image')


class ImageForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Party
        fields = ('image', 'x', 'y', 'width', 'height',)


class MembersImageForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Party
        fields = ('members_image', 'x', 'y', 'width', 'height',)
