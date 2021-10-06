from django.conf.urls import url
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
    url(
        r"^$",
        lambda request: redirect(
            "frontend:period", next(iter(dataviz.ALLOCATION_PERIODS.keys()))
        ),
    ),
    url(r"(?P<period>%s)/$" % _periods, dataviz.render, name="period"),
    url(
        r"(?P<period>%s)/" % _periods + r"(?P<scenario>%s)/$" % _scenarios,
        dataviz.render,
        name="scenario",
    ),
    url(r"^disclaimer/$", views.disclaimer, name="disclaimer"),
    url(r"^search/$", views.ProgrammeFacetedSearchView.as_view(), name="search"),
    url(
        r"^search/bilateralinitiative/$",
        views.BilateralInitiativesSearchView.as_view(),
        name="search_bilateralinitiative",
    ),
    url(
        r"^search/export/bilateralinitiative/$",
        views.BilateralInitiativeFacetedExportView.as_view(),
        name="bilateralinitiative_export",
    ),
    url(
        r"^search/programme/$",
        views.ProgrammeFacetedSearchView.as_view(),
        name="search_programme",
    ),
    url(
        r"^search/export/programme/$",
        views.ProgrammeFacetedExportView.as_view(),
        name="programme_export",
    ),
    url(
        r"^search/project/$",
        views.ProjectFacetedSearchView.as_view(),
        name="search_project",
    ),
    url(
        r"^search/export/project/$",
        views.ProjectFacetedExportView.as_view(),
        name="project_export",
    ),
    url(
        r"^search/organisation/$",
        views.OrganisationFacetedSearchView.as_view(),
        name="search_organisation",
    ),
    url(
        r"^search/export/organisation/$",
        views.OrganisationFacetedExportView.as_view(),
        name="organisation_export",
    ),
    url(r"^search/news/$", views.NewsFacetedSearchView.as_view(), name="search_news"),
    url(
        r"^search/export/news/$",
        views.NewsFacetedExportView.as_view(),
        name="news_export",
    ),
    url(
        r"^embed/(?P<scenario>[a-z]+)/(?P<component>[a-z][a-z_-]+[a-z]).js$",
        views.EmbedComponent.as_view(),
        name="embed",
    ),
    url(
        r"^embed/(?P<period>.+)/(?P<scenario>[a-z]+)/(?P<component>[a-z][a-z_-]+[a-z]).js$",
        views.EmbedComponent.as_view(),
        name="embed",
    ),
    url(r"^robots.txt$", views.RobotsView.as_view(), name="robots"),
    # [dev-only] sandbox for testing ui components
    url(r"^sandbox/$", views.sandbox, name="sandbox"),
    url(r"^embed_sandbox/$", views.embed_sandbox, name="embed_sandbox"),
    url(
        r"^embed_sandbox/(?P<period>.+)/(?P<scenario>[a-z]+)/(?P<component>[a-z][a-z_-]+[a-z])$",
        views.embed_sandbox,
        name="embed_sandbox",
    ),
    url(
        r"^embed_sandbox/(?P<scenario>[a-z]+)/(?P<component>[a-z][a-z_-]+[a-z])$",
        views.embed_sandbox,
        name="embed_sandbox",
    ),
]
