from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _

from tinySteps.forms.base.mixins import FormControlMixin

class CustomUserCreation_Form(UserCreationForm, FormControlMixin):
    """User registration form with email field"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': _('Enter your email address'),
            'autocomplete': 'email'
        })
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['username', 'password1', 'password2']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['class'] = 'form-control'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("This email is already registered! Please use a different email or try logging in."))
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class PasswordReset_Form(forms.Form, FormControlMixin):
    """Password reset form with username, email, and new password fields"""
    
    username = forms.CharField(
        label=_("Username"),
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': _('Enter your username'),
            'autocomplete': 'username',
        })
    )
    
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'placeholder': _('Enter your email address'),
            'autocomplete': 'email',
        })
    )
    
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={
            'placeholder': _('Enter new password'),
            'autocomplete': 'new-password',
        }),
        strip=False,
    )
    
    new_password2 = forms.CharField(
        label=_("Confirm new password"),
        widget=forms.PasswordInput(attrs={
            'placeholder': _('Confirm new password'),
            'autocomplete': 'new-password',
        }),
        strip=False,
    )
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        
        try:
            user = User.objects.get(username=username)
            if user.email != email:
                raise forms.ValidationError(_("The email does not correspond to the indicated user!"))
        except User.DoesNotExist:
            raise forms.ValidationError(_("There is no user with this username!"))
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords do not match."))
        
        return cleaned_data