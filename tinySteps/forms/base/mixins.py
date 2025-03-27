from django import forms
from django.utils.translation import gettext as _

class FormControlMixin:
    """Adds Bootstrap form-control class to all fields"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] += ' form-control'

class TextareaMixin:
    """Configures textarea fields with consistent styling"""
    
    def __init__(self, *args, rows=4, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['rows'] = rows

class FileMixin:
    """Configures file input fields with consistent styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.FileInput):
                field.widget.attrs['accept'] = 'image/*'