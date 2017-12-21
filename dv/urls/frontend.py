from django.conf.urls import url
from dv.views import frontend as views


urlpatterns = [
    url(r'^$', views.home, name='home'),

    url(r'^grants/$', views.grants, name='grants'),
    url(r'^partners/$', views.partners, name='partners'),
    url(r'^projects/$', views.projects, name='projects'),
    url(r'^disclaimer/$', views.disclaimer, name='disclaimer'),

    url(r'^search/$',
        views.ProgrammeFacetedSearchView.as_view(),
        name='search'),
    url(r'^search/programme/$',
        views.ProgrammeFacetedSearchView.as_view(),
        name='search_programme'),
    url(r'^search/programme/export/$',
        views.ProgrammeFacetedExportView.as_view(),
        name='programme_export'),

    url(r'^search/project/$',
        views.ProjectFacetedSearchView.as_view(),
        name='search_project'),
    url(r'^search/project/export/$',
        views.ProjectFacetedExportView.as_view(),
        name='project_export'),

    url(r'^search/organisation/$',
        views.OrganisationFacetedSearchView.as_view(),
        name='search_organisation'),
    url(r'^search/organisation/export/$',
        views.OrganisationFacetedExportView.as_view(),
        name='organisation_export'),

    url(r'^search/news/$',
        views.NewsFacetedSearchView.as_view(),
        name='search_news'),
    url(r'^search/news/export/$',
        views.NewsFacetedExportView.as_view(),
        name='news_export'),

    url(r'^embed/(?P<scenario>[a-z]+)/(?P<component>[a-z][a-z-]+[a-z]).js$',
        views.EmbedComponent.as_view(),
        name='embed'),
    url(r'^robots.txt/$', views.RobotsView.as_view(), name='robots'),
    # [dev-only] sandbox for testing ui components
    url(r'^sandbox/$', views.sandbox, name='sandbox'),
]
