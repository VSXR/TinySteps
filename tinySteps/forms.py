from django import forms
from .models import InfoRequest_Model, Milestone_Model

class InfoRequest_Form(forms.ModelForm):
    class Meta:
        model = InfoRequest_Model
        fields = ['name', 'email', 'message']

class Milestone_Form(forms.ModelForm):
    class Meta:
        model = Milestone_Model
        fields = ['title', 'achieved_date', 'description', 'photo']
        widgets = {
            'achieved_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
