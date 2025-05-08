from django import forms
from .models import *
from folders_words.models import *


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','age','country']
        
        
class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = ['code', 'is_native']
        widgets = {
            'code': forms.Select(attrs={
                'class': 'form-select language-select',
                'dir': 'rtl'
            }),
            'is_native': forms.CheckboxInput(attrs={
                'class': 'form-check-input native-checkbox',
            }),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data