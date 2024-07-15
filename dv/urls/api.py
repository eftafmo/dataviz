from django.conf import settings
from django.urls import re_path
from django.views.decorators.cache import cache_page

from dv.views import api as views
from dv.views import frontend as front_views


urlpatterns = [
    re_path(r"^test-sentry", views.test_sentry),
    re_path(
        r"^bilateral-initiatives.json",
        cache_page(settings.API_CACHE_SECONDS)(views.bilateral_initiatives),
        name="bilateral-initiatives",
    ),
    re_path(
        r"^overview.json",
        cache_page(settings.API_CACHE_SECONDS)(views.overview),
        name="index",
    ),
    re_path(
        r"^indicators.json",
        cache_page(settings.API_CACHE_SECONDS)(views.indicators),
        name="indicators",
    ),
    re_path(
        r"^grants.json",
        cache_page(settings.API_CACHE_SECONDS)(views.grants),
        name="grants",
    ),
    re_path(
        r"^sdg.json", cache_page(settings.API_CACHE_SECONDS)(views.sdg), name="goals"
    ),
    re_path(
        r"^projects.json",
        cache_page(settings.API_CACHE_SECONDS)(views.projects),
        name="projects",
    ),
    re_path(
        r"^partners.json",
        cache_page(settings.API_CACHE_SECONDS)(views.partners),
        name="partners",
    ),
    re_path(
        r"^grants/(?P<beneficiary>[A-Z]{2}).json",
        cache_page(settings.API_CACHE_SECONDS)(views.beneficiary_detail),
        name="grants-beneficiary-detail",
    ),
    re_path(
        r"^projects/(?P<beneficiary>[A-Z]{2}).json",
        cache_page(settings.API_CACHE_SECONDS)(views.projects_beneficiary_detail),
        name="projects-beneficiary-detail",
    ),
    re_path(
        r"^sdg/(?P<beneficiary>[A-Z]{2}).json",
        cache_page(settings.API_CACHE_SECONDS)(views.sdg_beneficiary_detail),
        name="sdg-beneficiary-detail",
    ),
    re_path(
        r"^projects/",
        views.ProjectList.as_view(),
        name="project-list",
    ),
    re_path(
        r"^search_programme_typeahead/$",
        front_views.ProgrammeTypeaheadFacetedSearchView.as_view(),
        name="search_programme_typeahead",
    ),
    re_path(
        r"^search_project_typeahead/$",
        front_views.ProjectTypeaheadFacetedSearchView.as_view(),
        name="search_project_typeahead",
    ),
    re_path(
        r"^search_organisation_typeahead/$",
        front_views.OrganisationTypeaheadFacetedSearchView.as_view(),
        name="search_organisation_typeahead",
    ),
    re_path(
        r"^search_news_typeahead/$",
        front_views.NewsTypeaheadFacetedSearchView.as_view(),
        name="search_news_typeahead",
    ),
]
