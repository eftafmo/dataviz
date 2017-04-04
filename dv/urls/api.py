from django.conf.urls import url
from dv.views import api as views


urlpatterns = [
    url(r'^allocation.csv', views.beneficiaries_fm_gross_allocation,
        name='beneficiary-allocation'),
    url(r'^sectors.json', views.sectors_areas_allocation,
        name='sector-allocation'),
]
