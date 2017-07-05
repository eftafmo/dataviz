import json5
from django.shortcuts import render
from haystack.generic_views import FacetedSearchView as BaseFacetedSearchView
from haystack.forms import FacetedSearchForm

from .search_form import EeaFacetedSearchForm

def home(request):
    return render(request, 'homepage.html')

def grants(request):
    return render(request, 'grants.html')

def partners(request):
    return render(request, 'partners.html')

def projects(request):
    return render(request, 'projects.html')

# def search(request):
#     return render(request, 'search.html')

def sandbox(request):
    return render(request, 'sandbox.html')


import logging
logger = logging.getLogger()


class FacetedSearchView(BaseFacetedSearchView):
    form_class = EeaFacetedSearchForm
    facet_fields = [
        'state_name',
        'programme_area_ss',
        'priority_sector_ss',
        'financial_mechanism_ss',
        'outcome_ss',
        'programme_name',
        'programme_status',
        'kind',
    ]
    template_name = 'search.html'
    paginate_by = 10
    context_object_name = 'object_list'
    # FIXME this does not seem to work anymore.
    initial = {
        'kind': ['Programme'],
    }

    def form_invalid(self, form):
        self.queryset = form.search()
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        object_list = kwargs.pop('object_list', self.queryset)
        context = super().get_context_data(object_list=object_list, **kwargs)
        # for o in context['object_list']:
        #     if isinstance(o.state_name, str):
        #         logger.warning(' +++', o.state_name, type(o.state_name))
        #         o.state_name = json5.loads(o.state_name)
        #     if isinstance(o.programme_name, str):
        #         o.programme_name = json5.loads(o.programme_name)
        return context
