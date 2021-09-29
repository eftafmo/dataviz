from django.conf import settings
from django.conf.urls import url
from django.views.decorators.cache import cache_page

from dv.views import api as views
from dv.views import frontend as front_views


urlpatterns = [
    url(r'^test-sentry', views.test_sentry),
    url(r'^bilateral-initiatives.json',
        cache_page(settings.API_CACHE_SECONDS)(views.bilateral_initiatives),
        name='bilateral-initiatives'),
    url(r'^overview.json',
        cache_page(settings.API_CACHE_SECONDS)(views.overview),
        name='index'),
    url(r'^grants.json',
        cache_page(settings.API_CACHE_SECONDS)(views.grants),
        name='grants'),
    url(r'^sdg.json',
        cache_page(settings.API_CACHE_SECONDS)(views.sdg),
        name='goals'),
    url(r'^projects.json',
        cache_page(settings.API_CACHE_SECONDS)(views.projects),
        name='projects'),
    url(r'^partners.json',
        cache_page(settings.API_CACHE_SECONDS)(views.partners),
        name='partners'),
    url(r'^grants/(?P<beneficiary>[A-Z]{2}).json',
        cache_page(settings.API_CACHE_SECONDS)(views.beneficiary_detail),
        name='grants-beneficiary-detail'),
    url(r'^projects/(?P<beneficiary>[A-Z]{2}).json',
        cache_page(settings.API_CACHE_SECONDS)(views.projects_beneficiary_detail),
        name='projects-beneficiary-detail'),

    url(r'^projects/',
        views.ProjectList.as_view(),
        name='project-list',
        ),
    url(r'^search_programme_typeahead/$',
        front_views.ProgrammeTypeaheadFacetedSearchView.as_view(),
        name='search_programme_typeahead'
        ),
    url(r'^search_project_typeahead/$',
        front_views.ProjectTypeaheadFacetedSearchView.as_view(),
        name='search_project_typeahead'
        ),
    url(r'^search_organisation_typeahead/$',
        front_views.OrganisationTypeaheadFacetedSearchView.as_view(),
        name='search_organisation_typeahead'
        ),
    url(r'^search_news_typeahead/$',
        front_views.NewsTypeaheadFacetedSearchView.as_view(),
        name='search_news_typeahead'
        ),
]
