# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db import models

from common.models import User
from .tasks import deactivate_advert


class Contact(models.Model):
    first_name = models.CharField(max_length=32, blank=True)
    last_name = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    token = models.CharField(max_length=8, blank=True)

    def __unicode__(self):
        return self.email if self.email else self.phone


class Advert(models.Model):
    tag = models.ManyToManyField('Tag', through='AdvertTag')
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    contact = models.OneToOneField(Contact, blank=True, null=True)
    title = models.CharField(max_length=32)
    text = models.TextField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)
    active_until = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    task = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title

    def has_changed(self, field):
        """
        Checks whether the specified field has changed in the model.
        """
        try:
            advert = self.__class__.objects.get(id=self.id)
        except ObjectDoesNotExist:
            return False
        else:
            if self.__getattribute__(field) != advert.__getattribute__(field):
                return True


class Tag(models.Model):
    title = models.CharField(max_length=16)

    def __unicode__(self):
        return self.title


class AdvertTag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT)
    advert = models.ForeignKey(Advert)

    def __unicode__(self):
        return 'AdvertTag {}'.format(self.id)


@receiver(pre_save, sender=Advert)
def deactivate_task_pre(sender, instance, **kwargs):
    """
    Send task for deactivate Advert if an instance has been changed.
    """
    if instance.has_changed('active_until'):
        instance.task += 1
        deactivate_advert.apply_async((instance.pk, instance.task), eta=instance.active_until)


@receiver(post_save, sender=Advert)
def deactivate_task_post(sender, instance, **kwargs):
    """
    Send task for deactivate Advert if an instance has been created.
    """
    if kwargs['created']:
        deactivate_advert.apply_async((instance.pk, instance.task), eta=instance.active_until)
