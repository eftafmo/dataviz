from django.conf.urls import url
from dv.views import api as views


urlpatterns = [
    # TODO Add this back if you want to test api/grants.json without changing the UI.
    # TODO Remove them after the change
    # url(r'^allocation.csv', views.beneficiaries_fm_gross_allocation,
    #     name='beneficiary-fm-allocation'),
    # url(r'^sectors.json', views.sectors_areas_allocation,
    #     name='sector-allocation'),
    # url(r'^beneficiaries.csv', views.beneficiary_allocation,
    #     name='beneficiary-allocation'),
    url(r'^overview.json', views.overview, name='overview'),
    url(r'^grants.json', views.grants, name='grants'),
    url(r'^beneficiary-allocation/(?P<beneficiary>[A-Z]{2}).json',
        views.beneficiary_allocation_detail,
        name='beneficiary-allocation-detail'),

    url(r'^projects/',
        views.ProjectList.as_view(),
        name='project-list',
        ),
    url(r'^news.json', views.news, name='news'),
]
