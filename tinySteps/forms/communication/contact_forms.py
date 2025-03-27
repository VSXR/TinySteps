from django import forms
from django.utils.translation import gettext as _

from tinySteps.models import Contact_Model
from tinySteps.forms.base.mixins import FormControlMixin, TextareaMixin

class Contact_Form(forms.ModelForm, FormControlMixin, TextareaMixin):
    """Contact form for sending messages to site administrators"""
    
    class Meta:
        model = Contact_Model
        fields = ['name', 'email', 'message']
        widgets = {
            'message': forms.Textarea(),
        }
        labels = {
            'name': _('Name'),
            'email': _('Email'),
            'message': _('Message'),
        }