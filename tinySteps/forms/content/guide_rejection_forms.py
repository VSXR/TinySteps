from django import forms
from django.utils.translation import gettext as _

class GuideRejection_Form(forms.Form):
    """Form to reject a guide"""
    
    rejection_reason = forms.CharField(
        label=_("Rejection reason"),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _("Please explain why this guide is being rejected...")
        }),
        required=True,
        help_text=_("This feedback will be sent to the author.")
    )
    
    internal_notes = forms.CharField(
        label=_("Internal notes"),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': _("Optional internal notes (not sent to the author)")
        }),
        required=False,
        help_text=_("These notes are for staff only and won't be shared with the author.")
    )
    
    def clean_rejection_reason(self):
        reason = self.cleaned_data.get('rejection_reason', '')
        if len(reason) < 10:
            raise forms.ValidationError(_("Please provide a more detailed rejection reason (at least 10 characters)."))
        return reason