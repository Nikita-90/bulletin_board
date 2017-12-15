# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Advert, AdvertTag, Contact, Tag


class AdvertTagInline(admin.TabularInline):
    model = AdvertTag
    extra = 1


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    fields = ('first_name', 'last_name', 'email', 'phone',)
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone', 'token',)


@admin.register(Advert)
class AdvertAdmin(admin.ModelAdmin):
    fields = ('contact', 'user', 'title', 'text', 'active_until', 'is_active',)
    list_display = ('id', 'contact', 'user', 'title', 'text', 'active_until', 'is_active', 'task')
    inlines = (AdvertTagInline,)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fields = ('title',)
    list_display = ('id', 'title',)


@admin.register(AdvertTag)
class AdvertTagAdmin(admin.ModelAdmin):
    fields = ('tag', 'advert',)
    list_display = ('id', 'tag', 'advert',)
