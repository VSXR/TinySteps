from django import forms
from django.contrib.auth.models import User
from .models import InfoRequest_Model, PasswordReset_Model, Milestone_Model

class InfoRequest_Form(forms.ModelForm):
    class Meta:
        model = InfoRequest_Model
        fields = ['name', 'email', 'message']

class PasswordResetRequest_Form(forms.Form):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter your email address',
            'autocomplete': 'email',
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email, is_active=True).exists():
            # Don't reveal if email exists or not for security
            pass
        return email

class PasswordResetConfirm_Form(forms.Form):
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password',
        }),
        strip=False,
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password',
        }),
        strip=False,
    )
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields didn't match!")
        return password2
    
    def save(self):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        self.user.save()
        return self.user

class Milestone_Form(forms.ModelForm):
    class Meta:
        model = Milestone_Model
        fields = ['title', 'achieved_date', 'description', 'photo']
        widgets = {
            'achieved_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
