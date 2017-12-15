from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('bulletin_board_app.urls')),
    url(r'', include('common.urls')),
]
