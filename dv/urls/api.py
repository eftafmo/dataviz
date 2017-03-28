from django.conf.urls import url
from dv.views import api as views


urlpatterns = [
    url(r'^allocation.csv', views.beneficiaries_fm_gross_allocation, name='allocation'),
]
