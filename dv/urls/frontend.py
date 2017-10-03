from django.conf.urls import url
from dv.views import frontend as views


urlpatterns = [
    url(r'^$', views.home, name='home'),

    url(r'^grants/$', views.grants, name='grants'),
    url(r'^partners/$', views.partners, name='partners'),
    url(r'^projects/$', views.projects, name='projects'),

    url(r'^disclaimer/$', views.disclaimer, name='disclaimer'),

    # url(r'^search/$', views.FacetedSearchView.as_view(), name='search'),
    url(r'^search/$', views.ProgrammeFacetedSearchView.as_view(), name='search'),
    url(r'^search/programme/$', views.ProgrammeFacetedSearchView.as_view(), name='search_programme'),
    url(r'^search/project/$', views.ProjectFacetedSearchView.as_view(), name='search_project'),
    url(r'^search/organisation/$', views.OrganisationFacetedSearchView.as_view(), name='search_organisation'),
    url(r'^search/news/$', views.NewsFacetedSearchView.as_view(),
        name='search_news'),

    url(r'^embed/(?P<scenario>[a-z]+)/(?P<component>[a-z][a-z-]+[a-z]).js$',
        views.EmbedComponent.as_view(),
        name='embed'),

    # [dev-only] sandbox for testing ui components
    url(r'^sandbox/$', views.sandbox, name='sandbox'),
]
