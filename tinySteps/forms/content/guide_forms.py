from django import forms
from django.utils.translation import gettext as _

from tinySteps.models import Guides_Model
from tinySteps.forms.base.mixins import FormControlMixin, TextareaMixin, FileMixin

class GuideSubmission_Form(forms.ModelForm, FormControlMixin, TextareaMixin, FileMixin):
    """Form for submitting a new guide"""
    
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _('Add tags separated by commas (e.g., parenting, nutrition)')
        }),
        label=_('Tags')
    )

    image = forms.ImageField(
        required=True,
        label=_('Upload Image')
    )

    class Meta:
        model = Guides_Model
        fields = ['title', 'desc', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': _('Enter a clear title for your guide')
            }),
            'desc': forms.Textarea(attrs={
                'rows': 10,
                'placeholder': _('Share your knowledge and experience')
            }),
        }
        labels = {
            'title': _('Title'),
            'desc': _('Content'),
            'image': _('Image'),
        }

class GuideRejection_Form(forms.Form, FormControlMixin, TextareaMixin):
    """Form for rejecting a guide submission"""
    
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label=_("Rejection Reason"),
        help_text=_("Please explain why this guide is being rejected. This will be sent to the author."),
        required=True
    )