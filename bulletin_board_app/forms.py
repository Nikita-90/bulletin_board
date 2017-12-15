# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.admin.widgets import AdminSplitDateTime
from django import forms

from .models import Advert, AdvertTag, Contact, Tag


class AdvertFormPre(forms.ModelForm):
    active_until = forms.SplitDateTimeField(widget=AdminSplitDateTime)

    class Meta:
        model = Advert
        fields = ('title', 'text', 'is_active', 'active_until')


class AdvertForm(forms.ModelForm):
    active_until = forms.SplitDateTimeField(widget=AdminSplitDateTime)

    class Meta:
        model = Advert
        fields = ('title', 'text', 'is_active', 'contact', 'user', 'active_until')

    def __init__(self, *args, **kwargs):
        super(AdvertForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = self.fields['user'].hidden_widget()
        self.fields['contact'].widget = self.fields['contact'].hidden_widget()

    def clean(self):
        clean_data = super(AdvertForm, self).clean()
        if not (clean_data.get('user') or clean_data.get('contact')):
            raise forms.ValidationError('Залогиньтесь или сотавьте контактные данные')


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('first_name', 'last_name', 'email', 'phone', 'token',)

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['token'].widget = self.fields['token'].hidden_widget()

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone and not (phone[0] == '+' and phone[1:].isdigit()):
            raise forms.ValidationError('Номер телефона должен начинаться со знака "+" и содержать только цифры.')
        return phone

    def clean(self):
        clean_data = super(ContactForm, self).clean()
        if not (clean_data.get('email') or clean_data.get('phone')):
            raise forms.ValidationError({'email': 'Заполните номер телефона или email',
                                         'phone': 'Заполните номер телефона или email'})


