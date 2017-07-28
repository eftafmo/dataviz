import os.path
import re
from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from haystack.generic_views import FacetedSearchView as BaseFacetedSearchView
from webpack_loader import utils as webpack
from dv.lib import utils

from .search_form import EeaFacetedSearchForm, EeaAutoFacetedSearchForm

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
        'programme_status',
        'kind',
    ]
    template_name = 'search.html'
    paginate_by = 10
    context_object_name = 'object_list'

    def form_invalid(self, form):
        self.queryset = form.search()
        return super().form_invalid(form)

    # def get_context_data(self, *args, **kwargs):
    #     objls = kwargs.pop('object_list', self.queryset)
    #     ctx = super().get_context_data(object_list=objls, **kwargs)
    #     return ctx


class ProgrammeFacetedSearchView(FacetedSearchView):
    facet_fields = FacetedSearchView.facet_fields + [
        'outcome_ss',
    ]
    initial = {
        'kind': ['Programme'],
        # hack! we remove this at form init
        'view_name': 'ProgrammeFacetedSearchView'
    }


class ProjectFacetedSearchView(FacetedSearchView):
    facet_fields = FacetedSearchView.facet_fields + [
        'programme_name',
        'project_status',
        'geotarget',
    ]
    initial = {
        'kind': ['Project'],
        # hack! we remove this at form init
        'view_name': 'ProjectFacetedSearchView'
    }


class OrganisationFacetedSearchView(FacetedSearchView):
    facet_fields = FacetedSearchView.facet_fields + [
        'programme_name',
        'project_name',
        'country',
        'nuts',
        'org_type_category',
        'org_type',
        'role_ss',
    ]
    initial = {
        'kind': ['Organisation'],
        # hack! we remove this at form init
        'view_name': 'OrganisationFacetedSearchView'
    }


class _TypeaheadFacetedSearchView(object):
    form_class = EeaAutoFacetedSearchForm
    template_name = None

    def get_data(self, context):
        form = context['form']
        sqs = context[self.context_object_name]

        # we fish for values that match our search terms.
        # say, the user is looking for Programmes that are related to outcomes containing
        # words starting with green and familiy
        # and are also narrowed down to only kind:Programme, Poland Programmes, and EEA FM
        # we want to present to the js select2 multiselect only distinct, relevant values
        # and no more than a certain limit, 10 possibilities
        # TODO actually we look for term1 AND term2 match inside the CONCATENATION
        # TODO of all Programme's outcomes; because of this concatenation the user adding words
        # TODO will not necessarily improve his results: some words will fall inside one Outcome
        # TODO and some in other Outcome belonging to the same Programme. It will look like
        # TODO an AND match from our side but like an OR match from his side
        # TODO this will be fun to fix :(
        vals = set()
        terms = form.auto_value.lower().split()
        for res in sqs:
            vals = vals.union(form.matched_multi_values(res, terms))
            # limit this - we are going to ajax this often
            if len(vals) >= 20:
                break
        return {
            'results': [ {'text': val, 'id': val} for val in vals ],
            'results_for': form.auto_name,
            'total_count': len(vals),
        }

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(self.get_data(context), **response_kwargs)


class ProgrammeTypeaheadFacetedSearchView(_TypeaheadFacetedSearchView, ProgrammeFacetedSearchView):
    pass


class ProjectTypeaheadFacetedSearchView(_TypeaheadFacetedSearchView, ProjectFacetedSearchView):
    pass


class OrganisationTypeaheadFacetedSearchView(_TypeaheadFacetedSearchView, OrganisationFacetedSearchView):
    pass


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

        def geturl(f):
            url = f['url']
            if url.startswith('/'):
                url = '//' + self.request.get_host() + url
            return url

        context.update({
            'jsfiles': [geturl(f) for f in jsfiles],
            'cssfiles': [geturl(f) for f in cssfiles],
            'object': obj,
            'datasource': self.request.build_absolute_uri(
                reverse("api:" + scenario)
            ),
            'embedurl': self.request.build_absolute_uri(),
            'randomness': utils.mkrandstr(),
        })
        return context
