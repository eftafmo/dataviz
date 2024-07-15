from django.urls import re_path
from django.shortcuts import redirect
from dv.views import frontend as views
from dv.views import dataviz


_periods = "|".join(dataviz.ALLOCATION_PERIODS.keys())
# this is imprecise, but it's just a helper to do early 404
_scenarios = "|".join(
    {s for slist in dataviz.ALLOCATION_PERIODS.values() for s in slist}
)


urlpatterns = [
    # redirect homepage to latest allocation period
    re_path(
        r"^$",
        lambda request: redirect(
            "frontend:period", next(iter(dataviz.ALLOCATION_PERIODS.keys()))
        ),
    ),
    re_path(r"(?P<period>%s)/$" % _periods, dataviz.render, name="period"),
    re_path(
        r"(?P<period>%s)/" % _periods + r"(?P<scenario>%s)/$" % _scenarios,
        dataviz.render,
        name="scenario",
    ),
    re_path(r"^disclaimer/$", views.disclaimer, name="disclaimer"),
    re_path(r"^search/$", views.ProgrammeFacetedSearchView.as_view(), name="search"),
    re_path(
        r"^search/bilateralinitiative/$",
        views.BilateralInitiativesSearchView.as_view(),
        name="search_bilateralinitiative",
    ),
    re_path(
        r"^search/export/bilateralinitiative/$",
        views.BilateralInitiativeFacetedExportView.as_view(),
        name="bilateralinitiative_export",
    ),
    re_path(
        r"^search/programme/$",
        views.ProgrammeFacetedSearchView.as_view(),
        name="search_programme",
    ),
    re_path(
        r"^search/export/programme/$",
        views.ProgrammeFacetedExportView.as_view(),
        name="programme_export",
    ),
    re_path(
        r"^search/project/$",
        views.ProjectFacetedSearchView.as_view(),
        name="search_project",
    ),
    re_path(
        r"^search/export/project/$",
        views.ProjectFacetedExportView.as_view(),
        name="project_export",
    ),
    re_path(
        r"^search/organisation/$",
        views.OrganisationFacetedSearchView.as_view(),
        name="search_organisation",
    ),
    re_path(
        r"^search/export/organisation/$",
        views.OrganisationFacetedExportView.as_view(),
        name="organisation_export",
    ),
    re_path(
        r"^search/news/$", views.NewsFacetedSearchView.as_view(), name="search_news"
    ),
    re_path(
        r"^search/export/news/$",
        views.NewsFacetedExportView.as_view(),
        name="news_export",
    ),
    re_path(
        r"^embed/(?P<scenario>[a-z]+)/(?P<component>[a-z][a-z_-]+[a-z]).js$",
        views.EmbedComponent.as_view(),
        name="embed",
    ),
    re_path(
        r"^embed/(?P<period>.+)/(?P<scenario>[a-z]+)/(?P<component>[a-z][a-z_-]+[a-z]).js$",
        views.EmbedComponent.as_view(),
        name="embed",
    ),
    re_path(r"^robots.txt$", views.RobotsView.as_view(), name="robots"),
    # [dev-only] sandbox for testing ui components
    re_path(r"^sandbox/$", views.sandbox, name="sandbox"),
    re_path(r"^embed_sandbox/$", views.embed_sandbox, name="embed_sandbox"),
    re_path(
        r"^embed_sandbox/(?P<period>.+)/(?P<scenario>[a-z]+)/(?P<component>[a-z][a-z_-]+[a-z])$",
        views.embed_sandbox,
        name="embed_sandbox",
    ),
    re_path(
        r"^embed_sandbox/(?P<scenario>[a-z]+)/(?P<component>[a-z][a-z_-]+[a-z])$",
        views.embed_sandbox,
        name="embed_sandbox",
    ),
]
