from django.conf.urls import url
from dv.views import frontend as views


urlpatterns = [
    url(r'^$', views.home, name='home'),

    url(r'^grants/$', views.grants, name='grants'),
    url(r'^partners/$', views.partners, name='partners'),
    url(r'^projects/$', views.projects, name='projects'),

    url(r'^search/$', views.FacetedSearchView.as_view(), name='haystack_search'),

    url(r'^embed/(?P<scenario>[a-z]+)/(?P<component>[a-z][a-z-]+[a-z]).js$',
        views.EmbedComponent.as_view(),
        name='embed'),

    # [dev-only] sandbox for testing ui components
    url(r'^sandbox/$', views.sandbox, name='sandbox'),
]
