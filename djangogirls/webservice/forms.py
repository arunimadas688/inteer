#files.py
import re

from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import UserProfile
from django.utils.translation import ugettext_lazy as _

class RegistrationForm(forms.Form):

    username = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs={'required': 'True', 'max_length': '30', 'class': 'form-control', 'placeholder': 'Username'}), label=_("Username"), error_messages={ 'invalid': _("Username must contain only letters, numbers and underscores.") })
    ns_fname = forms.CharField(widget=forms.TextInput(attrs={'required': 'True', 'max_length': '30', 'class': 'form-control', 'placeholder': 'FirstName'}))
    ns_lname = forms.CharField(widget=forms.TextInput(attrs={'required': 'True', 'max_length': '30', 'class': 'form-control', 'placeholder': 'LastName'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'required': 'True', 'max_length': '30', 'class': 'form-control', 'placeholder': 'Email'}), label=_("Email address"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'required': 'True', 'max_length': '30', 'class': 'form-control', 'placeholder': 'Password', 'render_value': 'False'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'required': 'True', 'max_length': '30', 'class': 'form-control', 'placeholder': 'ConfirmPassword', 'render_value': 'False'}))
    def clean_username(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_("The username already exists. Please try another one."))

    def clean_email(self):
        try:
            user = User.objects.get(email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError(_("The email already exists. Please try another one."))

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields did not match."))
        return self.cleaned_data

