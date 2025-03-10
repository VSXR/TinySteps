from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import InfoRequest_Model,PasswordReset_Model, Milestone_Model

class InfoRequest_Form(forms.ModelForm):
    class Meta:
        model = InfoRequest_Model
        fields = ['name', 'email', 'message']

class Milestone_Form(forms.ModelForm):
    class Meta:
        model = Milestone_Model
        fields = ['title', 'achieved_date', 'description', 'photo']
        widgets = {
            'achieved_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class PasswordReset_Form(forms.Form):
    username = forms.CharField(
        label="Username",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autocomplete': 'username',
        })
    )
    
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter your email address',
            'autocomplete': 'email',
        })
    )
    
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password',
        }),
        strip=False,
    )
    
    new_password2 = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
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
        
        # Verificar que el usuario existe y el email coincide
        try:
            user = User.objects.get(username=username)
            if user.email != email:
                raise forms.ValidationError("El email no corresponde al usuario indicado.")
        except User.DoesNotExist:
            raise forms.ValidationError("No existe un usuario con este nombre de usuario.")
        
        # Verificar que las contraseñas coinciden
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data

class CustomUserCreation_Form(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email ya está registrado. Por favor usa otro email o intenta iniciar sesión.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


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
    
    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user