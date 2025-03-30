from django import forms
from django.utils.translation import gettext as _
from tinySteps.models import Guides_Model, Category_Model
from tinySteps.forms.base.mixins import FormControlMixin, TextareaMixin, FileMixin

class GuideSubmission_Form(forms.ModelForm, FormControlMixin, TextareaMixin, FileMixin):
    """Form for submitting a new guide"""
    
    category = forms.ModelChoiceField(
        queryset=Category_Model.objects.all().order_by('name'),
        empty_label=_("Select a category"),
        required=False,
        label=_("Category"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'tag-hidden-input form-control',
            'data-role': 'tagsinput'
        }),
        label=_('Tags')
    )

    image = forms.ImageField(
        required=True,
        label=_('Featured Image'),
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/jpeg,image/png'
        })
    )
    
    summary = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_('Summary')
    )

    class Meta:
        model = Guides_Model
        fields = ['title', 'summary', 'category', 'desc', 'image', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'}),
            'desc': forms.Textarea(attrs={'rows': 10, 'class': 'form-control rich-text-editor'})
        }
    
    def __init__(self, *args, **kwargs):
        guide_type = kwargs.pop('guide_type', 'parent')
        super().__init__(*args, **kwargs)
        
        # Filter categories by guide type
        if guide_type:
            try:
                self.fields['category'].queryset = Category_Model.objects.filter(
                    guide_type=guide_type
                ).order_by('name')
            except:
                pass
    
    def get_tag_categories(self, guide_type):
        """Get predefined tag categories for the guide type"""
        from tinySteps.models import Guides_Model
        
        predefined_tags = Guides_Model.PREDEFINED_TAGS.get(guide_type, {})
        if guide_type == 'parent':
            tag_categories = {
                'Basic': ['parenting', 'childcare', 'development', 'education'],
                'Ages': ['newborn', 'infant', 'toddler', 'preschool'],
                'Topics': ['sleep', 'discipline', 'health', 'activities']
            }
        else:  # nutrition
            tag_categories = {
                'Basic': ['nutrition', 'diet', 'health', 'recipes'],
                'Food Types': ['vegetables', 'fruits', 'proteins', 'grains'],
                'Ages': ['baby food', 'toddler meals', 'kids meals']
            }
        
        return tag_categories

    def clean_title(self):
        title = self.cleaned_data.get('title', '')
        if len(title) < 5:
            raise forms.ValidationError(_('Title must be at least 5 characters long.'))
        return title
    
    def clean_desc(self):
        desc = self.cleaned_data.get('desc', '')
        if len(desc) < 300:
            raise forms.ValidationError(_('Content must be at least 300 characters long.'))
        return desc

class GuideRejection_Form(forms.Form, FormControlMixin, TextareaMixin):
    """Form for rejecting a guide submission"""
    
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label=_("Rejection Reason"),
        help_text=_("Please explain why this guide is being rejected. This will be sent to the author."),
        required=True
    )