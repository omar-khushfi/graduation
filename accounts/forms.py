from django import forms
from .models import User

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','age','country']