from django.conf.urls import url
from dv.views import frontend as views


urlpatterns = [
    url(r'^$', views.home, name='home'),

    # [dev-only] sandbox for testing ui components
    url(r'^search/$', views.search, name='search'),

    # [dev-only] sandbox for testing ui components
    url(r'^sandbox/$', views.sandbox, name='sandbox'),
]

