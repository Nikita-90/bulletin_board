from __future__ import unicode_literals
from django.conf.urls import url

import views

app_name = 'common'

urlpatterns = [
    url(r'^registration/$', views.registration, name='registration'),
    url(r'^authentication_user/$', views.authentication_user, name='authentication_user'),
    url(r'^logout/$', views.logout_view, name='logout_view'),
]
