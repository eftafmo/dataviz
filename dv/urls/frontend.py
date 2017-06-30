from django.conf.urls import url
from dv.views import frontend as views


urlpatterns = [
    url(r'^$', views.home, name='home'),

    url(r'^grants/$', views.grants, name='grants'),
    url(r'^partners/$', views.partners, name='partners'),
    url(r'^projects/$', views.projects, name='projects'),

    url(r'^search/$', views.FacetedSearchView.as_view(), name='haystack_search'),

    # [dev-only] sandbox for testing ui components
    url(r'^sandbox/$', views.sandbox, name='sandbox'),
]
