from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import api, frontend


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include((api, 'api'))),
    url(r'^', include((frontend, 'frontend'))),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
