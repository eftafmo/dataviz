from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from . import api, frontend


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include((api, "api"))),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("", include((frontend, "frontend"))),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
