from django import forms
from django.contrib.auth.models import User
from app_admin.models import *

class FormUser(forms.ModelForm):
    username=forms.CharField(label='Username',widget=forms.TextInput(attrs={
        'class':'form-control'
    }))
    email=forms.CharField(label='Email',widget=forms.EmailInput(attrs={
        'class':'form-control'
    }))
    password=forms.CharField(label='Password',widget=forms.PasswordInput(attrs={
        'class':'form-control'
    }))
    confirm_password=forms.CharField(label='Confirm Password',widget=forms.PasswordInput(attrs={
        'class':'form-control'
    }))
    first_name=forms.CharField(label='First Name',widget=forms.TextInput(attrs={
        'class':'form-control'
    }))
    last_name=forms.CharField(label='Last Name',widget=forms.TextInput(attrs={
        'class':'form-control'
    }))

    class Meta:
        model=User
        fields=['username','email','password','first_name','last_name']

class FormUserProfileInfo(forms.ModelForm):
    portfolio=forms.URLField(label='Portfolio', widget=forms.TextInput(attrs={
        'class':'form-control'
    }))
    image=forms.ImageField(label='Image', required=False,widget=forms.FileInput(attrs={
        'class':'form-control-file'
    }))

    class Meta:
        model=UserProfileInfo
        exclude=['user']