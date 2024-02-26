from django import forms
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget

class NewArticleForm(forms.Form):
    text = forms.CharField(label="", help_text="", widget=SummernoteWidget(attrs={'style': 'width:100%;',}))