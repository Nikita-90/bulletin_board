# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import User


class BaseUserForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BaseUserForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs['placeholder'] = self.fields[field].label
            self.fields[field].label = ''
            self.fields[field].help_text = ''


class UserCreatorForm(forms.ModelForm, BaseUserForm):
    password1 = forms.CharField(min_length=6, max_length=50, label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(min_length=6, max_length=50, label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone and not (phone[0] == '+' and phone[1:].isdigit()):
            raise forms.ValidationError('The Phone number must start with a "+" sign and have only digits.')
        return phone

    def save(self, commit=True):
        user = super(UserCreatorForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(BaseUserForm, forms.Form):
    email = forms.EmailField(label="Email address", max_length=255)
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': "Please enter a correct %(username)s and password. "
                         "Note that both fields may be case-sensitive.",
        'inactive': "This account is inactive.",
    }

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if email and password:
            try:
                self.user_cache = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError('Password or email is incorrect.', code='invalid_login')
            if not self.user_cache.check_password(password):
                raise forms.ValidationError('Password or email is incorrect.', code='invalid_login')