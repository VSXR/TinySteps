from django import forms
from django.utils.translation import gettext as _

class GuideRejection_Form(forms.Form):
    """Formulario para rechazar una guía"""
    
    rejection_reason = forms.CharField(
        label=_("Motivo de rechazo"),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _("Por favor explica por qué esta guía está siendo rechazada...")
        }),
        required=True,
        help_text=_("Este feedback será enviado al autor.")
    )
    
    internal_notes = forms.CharField(
        label=_("Notas internas"),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': _("Notas internas opcionales (no se envían al autor)")
        }),
        required=False,
        help_text=_("Estas notas son solo para el personal y no se compartirán con el autor.")
    )
    
    def clean_rejection_reason(self):
        reason = self.cleaned_data.get('rejection_reason', '')
        if len(reason) < 10:
            raise forms.ValidationError(_("Por favor proporciona un motivo de rechazo más detallado (al menos 10 caracteres)."))
        return reason