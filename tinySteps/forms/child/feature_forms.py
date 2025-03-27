from django import forms
from django.utils.translation import gettext as _

from tinySteps.models import Milestone_Model, Vaccine_Model, CalendarEvent_Model
from tinySteps.forms.base.mixins import FormControlMixin, TextareaMixin

class Milestone_Form(forms.ModelForm, FormControlMixin, TextareaMixin):
    """Form for creating and updating child milestones"""
    
    class Meta:
        model = Milestone_Model
        fields = ['title', 'achieved_date', 'description', 'photo']
        widgets = {
            'achieved_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(),
        }
        labels = {
            'title': _('Title'),
            'achieved_date': _('Achieved Date'),
            'description': _('Description'),
            'photo': _('Photo'),
        }

class Vaccine_Form(forms.ModelForm, FormControlMixin, TextareaMixin):
    """Form for creating and updating vaccine records"""
    
    class Meta:
        model = Vaccine_Model
        fields = ['name', 'date', 'administered', 'next_dose_date', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _('Vaccine name')}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'next_dose_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'placeholder': _('Additional information about the vaccine')}),
        }
        labels = {
            'name': _('Vaccine Name'),
            'date': _('Date'),
            'administered': _('Administered'),
            'next_dose_date': _('Next Dose Date (if any)'),
            'notes': _('Notes'),
        }
        
class CalendarEvent_Form(forms.ModelForm, FormControlMixin, TextareaMixin):
    """Form for creating and updating calendar events"""
    
    class Meta:
        model = CalendarEvent_Model
        fields = ['title', 'type', 'date', 'time', 'description', 'has_reminder', 'reminder_minutes']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': _('Event title')}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'placeholder': _('Event details'), 'rows': 3}),
        }
        labels = {
            'title': _('Event Title'),
            'type': _('Event Type'),
            'date': _('Date'),
            'time': _('Time'),
            'description': _('Description'),
            'has_reminder': _('Set Reminder'),
            'reminder_minutes': _('Reminder (minutes before)'),
        }