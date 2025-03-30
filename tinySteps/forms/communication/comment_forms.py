from django import forms
from django.utils.translation import gettext as _

from tinySteps.forms.base.mixins import FormControlMixin, TextareaMixin

class CommentFormBase(forms.Form, FormControlMixin, TextareaMixin):
    """Base class for all comment forms"""
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': _('Add a comment...'),
            'rows': 3
        }),
        label=_('Comment')
    )

class ForumComment_Form(CommentFormBase):
    """Comment form for forum posts"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css_class = 'form-control'
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += f' {css_class}'
            else:
                field.widget.attrs['class'] = css_class

class GuideComment_Form(CommentFormBase):
    """Comment form for guides"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css_class = 'form-control'
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += f' {css_class}'
            else:
                field.widget.attrs['class'] = css_class