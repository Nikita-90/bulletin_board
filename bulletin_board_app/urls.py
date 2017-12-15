from django.conf.urls import include, url
from django.views.i18n import javascript_catalog

import views

app_name = 'bulletin_board_app'

urlpatterns = [
    url(r'^advert/(?P<page>[0-9]+)/$', views.index, name='index'),
    url(r'^add_advert/$', views.add_advert, name='add_advert'),
    url(r'^advert_detail/(?P<advert_pk>\d+)/$', views.view_advert_detail, name='view_advert_detail'),
    url(r'^home_page/(?P<page>[0-9]+)/$', views.home_page, name='home_page'),
    url(r'^edit_my_advert/(?P<advert_pk>\d+)/$', views.edit_my_advert, name='edit_my_advert'),
    url(r'^docs/$', views.docs, name='docs'),
    url(r'^jsi18n', javascript_catalog, name='jsi18n'),
]
