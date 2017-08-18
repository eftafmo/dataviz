from django.conf.urls import url
from dv.views import api as views
from dv.views import frontend as front_views


urlpatterns = [
    # TODO Add this back if you want to test api/grants.json without changing the UI.
    # TODO Remove them after the change
    # url(r'^allocation.csv', views.beneficiaries_fm_gross_allocation,
    #     name='beneficiary-fm-allocation'),
    # url(r'^sectors.json', views.sectors_areas_allocation,
    #     name='sector-allocation'),
    # url(r'^beneficiaries.csv', views.beneficiary_allocation,
    #     name='beneficiary-allocation'),
    url(r'^overview.json', views.overview, name='index'),
    url(r'^grants.json', views.grants, name='grants'),
    url(r'^projects.json', views.projects, name='projects'),
    url(r'^partners.json', views.partners, name='partners'),
    url(r'^grants/(?P<beneficiary>[A-Z]{2}).json',
        views.beneficiary_detail,
        name='grants-beneficiary-detail'),

    url(r'^projects/(?P<beneficiary>[A-Z]{2}).json',
        views.projects_beneficiary_detail,
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
]
