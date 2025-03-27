from django import forms
from django.utils.translation import gettext as _

from tinySteps.models import ParentsForum_Model
from tinySteps.forms.base.mixins import FormControlMixin, TextareaMixin

class ForumPost_Form(forms.ModelForm, FormControlMixin, TextareaMixin):
    """Form for creating and updating forum posts"""
    
    class Meta:
        model = ParentsForum_Model
        fields = ['title', 'desc', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': _('Enter a title for your discussion')}),
            'desc': forms.Textarea(attrs={'rows': 6, 'placeholder': _('Share your experience, question, or advice')}),
        }
        labels = {
            'title': _('Discussion Title'),
            'desc': _('Your Message'),
            'category': _('Category / Hashtag')
        }