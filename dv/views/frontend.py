import json5
import os.path
import re
from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from haystack.generic_views import FacetedSearchView as BaseFacetedSearchView
from haystack.forms import FacetedSearchForm
from webpack_loader import utils as webpack
from dv.lib import utils

from .search_form import EeaFacetedSearchForm


SCENARIOS = (
    'index',
    'grants',
    'partners',
    'projects',
)


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


_COMPONENTS_DEFS_FILE = os.path.join(settings.BASE_DIR,
                                     "assets/js/root-instances.js")
_COMPONENTS_MATCH = re.compile(
    r"""
        (?:^|\s) const \s+ (%s) \s* = \s* [^\{]+ {
            (?:.*?,)? \s*
            components: \s* {
                \s* ([^\}]+) \s*
            }
    """ % '|'.join(map(str.capitalize, SCENARIOS)),
    flags=re.DOTALL | re.VERBOSE)

_COMPONENTS = {}
if not _COMPONENTS:
    with open(_COMPONENTS_DEFS_FILE) as f:
        content = f.read()

    scenarios = {}
    for scenario, compstr in _COMPONENTS_MATCH.findall(content):
        scenario = scenario.lower()
        components = {}

        for comp in map(str.strip, compstr.split(',')):
            if comp == "":
                continue

            name, obj = comp.split(':')
            name = name.strip().strip('"\'')
            obj = obj.strip()

            components[name] = obj

        _COMPONENTS[scenario] = components

class EmbedComponent(TemplateView):
    content_type = "text/javascript"
    template_name = "embed.js"
    template_engine = "jinja2"
    # TODO: must not cache

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        scenario = context['scenario']
        component = context['component']

        try:
            obj = _COMPONENTS[scenario][component]
        except KeyError:
            raise Http404

        jsfiles = webpack.get_files('scripts', 'js')
        cssfiles = webpack.get_files('styles', 'css')

        context.update({
            'jsfiles': [f['url'] for f in jsfiles],
            'cssfiles': [f['url'] for f in cssfiles],
            'object': obj,
            'datasource': self.request.build_absolute_uri(
                reverse("api:" + scenario)
            ),
            'embedurl': self.request.build_absolute_uri(),
            'randomness': utils.mkrandstr(),
        })
        return context
