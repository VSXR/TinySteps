from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _
from .models import Contact_Model, PasswordReset_Model, Milestone_Model, YourChild_Model

class CustomUserCreation_Form(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your email address'),
            'autocomplete': 'email'
        })
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)
    
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

class PasswordReset_Form(forms.Form):
    username = forms.CharField(
        label=_("Username"),
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your username'),
            'autocomplete': 'username',
        })
    )
    
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': _('Enter your email address'),
            'autocomplete': 'email',
        })
    )
    
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter new password'),
            'autocomplete': 'new-password',
        }),
        strip=False,
    )
    
    new_password2 = forms.CharField(
        label=_("Confirm new password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
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

# Model Forms
class YourChild_Form(forms.ModelForm):
    class Meta:
        model = YourChild_Model
        fields = ['name', 'second_name', 'birth_date', 'gender', 'age', 
                  'weight', 'height', 'desc', 'image', 'image_url']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'desc': forms.Textarea(attrs={'rows': 4}),
            'image': forms.FileInput(attrs={'accept': 'image/*'}),
            'image_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
        }
        labels = {
            'name': _('Name'),
            'second_name': _('Second Name'),
            'birth_date': _('Birth Date'),
            'gender': _('Gender'),
            'age': _('Age'),
            'weight': _('Weight'),
            'height': _('Height'),
            'desc': _('Description'),
            'image': _('Image'),
            'image_url': _('Image URL'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['second_name'].required = False
        self.fields['weight'].required = False
        self.fields['height'].required = False
        self.fields['desc'].required = False
        self.fields['image'].required = False
        self.fields['image_url'].required = False
        
        self.fields['image'].help_text = _("Upload a photo from your device")
        self.fields['image_url'].help_text = _("Or provide a URL to an image")
        self.fields['desc'].help_text = _("Additional information about your child")

class Milestone_Form(forms.ModelForm):
    class Meta:
        model = Milestone_Model
        fields = ['title', 'achieved_date', 'description', 'photo']
        widgets = {
            'achieved_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'title': _('Title'),
            'achieved_date': _('Achieved Date'),
            'description': _('Description'),
            'photo': _('Photo'),
        }

class Contact_Form(forms.ModelForm):
    class Meta:
        model = Contact_Model
        fields = ['name', 'email', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'name': _('Name'),
            'email': _('Email'),
            'message': _('Message'),
        }
