from django.conf.urls import url
from dv.views import frontend as views


urlpatterns = [
    url(r'^$', views.home, name='home'),
]
