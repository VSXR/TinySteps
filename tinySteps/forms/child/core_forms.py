from django import forms
from django.utils.translation import gettext as _

from tinySteps.models import YourChild_Model
from tinySteps.forms.base.mixins import FormControlMixin, TextareaMixin, FileMixin

class YourChild_Form(forms.ModelForm, FormControlMixin, TextareaMixin, FileMixin):
    """Form for creating and updating child information"""
    
    class Meta:
        model = YourChild_Model
        fields = ['name', 'second_name', 'birth_date', 'gender', 'age', 
                  'weight', 'height', 'desc', 'image', 'image_url']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'desc': forms.Textarea(),
            'image_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
        }
        labels = {
            'name': _('Name'),
            'second_name': _('Second Name'),
            'birth_date': _('Birth Date'),
            'gender': _('Gender'),
            'age': _('Age'),
            'weight': _('Weight'),
            'height': _('Height'),
            'desc': _('Description'),
            'image': _('Image'),
            'image_url': _('Image URL'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['second_name'].required = False
        self.fields['weight'].required = False
        self.fields['height'].required = False
        self.fields['desc'].required = False
        self.fields['image'].required = False
        self.fields['image_url'].required = False
        
        self.fields['image'].help_text = _("Upload a photo from your device")
        self.fields['image_url'].help_text = _("Or provide a URL to an image")
        self.fields['desc'].help_text = _("Additional information about your child")