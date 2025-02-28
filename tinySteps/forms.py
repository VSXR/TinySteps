from django import forms
from .models import InfoRequestModel

class InfoRequestForm(forms.ModelForm):
    class Meta:
        model = InfoRequestModel
        fields = ['name', 'email', 'phone', 'message']
