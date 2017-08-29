import os.path
import re
from collections import defaultdict

from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from haystack.generic_views import FacetedSearchView as BaseFacetedSearchView
from haystack.generic_views import FacetedSearchMixin as BaseFacetedSearchMixin
from webpack_loader import utils as webpack
from dv.lib import utils
from dv.models import (
    StaticContent,
    ProgrammeArea,
    State,
)

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

def disclaimer(request):
    content = StaticContent.objects.filter(name='Disclaimer')
    context = dict(body=content[0].body if content else None)
    return render(request, 'disclaimer.html', context)

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
        'programme_name',
        'kind',
    ]
    template_name = 'search.html'
    paginate_by = 10
    context_object_name = 'object_list'

    def form_invalid(self, form):
        self.queryset = form.search()
        return super().form_invalid(form)

    def get_paginate_by(self, queryset):
        return self.request.GET.get('paginate_by', self.paginate_by)

    PRG_STATUS_SORT = {
        'implementation': 0,
        'closed': 1,
        'approved': 2,
        'withdrawn': 3,
        'returned to po': 4,
    }
    PRJ_STATUS_SORT = {
        'in progress': 0,
        'completed': 1,
        'non completed': 2,
        'terminated': 3,
    }
    AREAS_LIST = ProgrammeArea.objects.order_by(
        '-order'
    ).values(
        'name', 'priority_sector__name', 'order'
    )
    # sort by -order because there are some duplicated names and we need the first occurrence only
    AREAS_SORT = dict([(x['name'].lower(), x['order']) for x in AREAS_LIST])
    SECTORS_SORT = dict([(x['priority_sector__name'].lower(), x['order']) for x in AREAS_LIST])
    ORG_ROLE_SORT = {
        'national focal point': 0,
        'programme operator': 1,
        'donor programme partner': 2,
        'project promoter': 3,
        'donor project partner': 4,
        'programme partner': 5,
        'project partner': 6,
    }

    REORDER_FACETS = {
        'programme_status': PRG_STATUS_SORT,
        'project_status': PRJ_STATUS_SORT,
        'programme_area_ss': AREAS_SORT,
        'priority_sector_ss': SECTORS_SORT,
        'role_ss': ORG_ROLE_SORT,
    }

    def reorder_facets(self, facets):
        for facet, order in self.REORDER_FACETS.items():
            if facet in facets:
                facets[facet] = sorted(
                    facets[facet],
                    key=lambda x: order.get(x[0].lower(), 99)
                )

    def get_context_data(self, *args, **kwargs):
        objls = kwargs.pop('object_list', self.queryset)
        ctx = super().get_context_data(object_list=objls, **kwargs)
        ctx['page_sizes'] = [10, 25, 50, 100]

        # Custom sorting of some facets, refs #326
        self.reorder_facets(ctx.get('facets', {}).get('fields', {}))

        return ctx

    def get_queryset(self):
        qs = super(BaseFacetedSearchMixin, self).get_queryset()
        for field in self.facet_fields:
            qs = qs.facet(field, limit=10000, sort='index')
        return qs


class ProgrammeFacetedSearchView(FacetedSearchView):
    facet_fields = FacetedSearchView.facet_fields + [
        'programme_status',
        'outcome_ss',
    ]
    initial = {
        'kind': ['Programme'],
        # hack! we remove this at form init
        'view_name': 'ProgrammeFacetedSearchView'
    }

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        # Add more utilities
        areas_dict = dict(ProgrammeArea.objects.all().values_list(
            'name',
            'priority_sector__name',
        ))
        # Group programme areas by sector
        for obj in ctx['object_list']:
            areas_by_sector = defaultdict(list)
            for area in obj.programme_area_ss:
                areas_by_sector[areas_dict[area]].append(area)
            obj.areas_by_sector = areas_by_sector
        return ctx


class ProjectFacetedSearchView(FacetedSearchView):
    facet_fields = ProgrammeFacetedSearchView.facet_fields + [
        'project_status',
        'geotarget',
        'theme_ss',
    ]
    initial = {
        'kind': ['Project'],
        # hack! we remove this at form init
        'view_name': 'ProjectFacetedSearchView'
    }


class OrganisationFacetedSearchView(FacetedSearchView):
    facet_fields = FacetedSearchView.facet_fields + [
        'project_name',
        'country',
        'city',
        'geotarget',
        'org_type_category',
        'org_type',
        'role_ss',
    ]
    initial = {
        'kind': ['Organisation'],
        # hack! we remove this at form init
        'view_name': 'OrganisationFacetedSearchView'
    }

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        # Add donor and beneficiary states - need to check if show flag
        states = list(State.objects.exclude(
            code='IN',
        ).values_list(
            'name',
            flat=True,
        ))
        #states.extend(['Liechtenstein', 'Norway', 'Iceland'])
        states.extend(utils.EEA_DONOR_STATES.keys())
        ctx['states_with_flags'] = states

        # Group programmes and projects by organisation roles
        for res in ctx['object_list']:
            d = defaultdict(list)
            if not res.object:
                # inconsistent index, obj deleted from db but present in Solr
                logger.warn('Inconsistent object in index: %s' % (res.id,))
                continue
            org_roles = res.object.roles.all()
            for org_role in org_roles:
                role_name = org_role.organisation_role.role
                if org_role.programme.is_tap:
                    continue
                prg_or_prj = org_role.programme
                if org_role.project:
                    prg_or_prj = org_role.project
                d[role_name].append('{} - {}'.format(prg_or_prj.code, prg_or_prj.name))
            for role, plist in d.items():
                d[role] = sorted(plist)
            res.prep_roles = dict(d)
        return ctx


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

        props = {
            'datasource': self.request.build_absolute_uri(
                reverse("api:" + scenario)
            ),
        }

        # this is ugly, nasty and not nice
        if scenario in ("grants", "projects"):
            props['detailsDatasource'] = self.request.build_absolute_uri(
                reverse("api:%s-beneficiary-detail" % scenario, args=("XX",))
            )

        context.update({
            'jsfiles': [geturl(f) for f in jsfiles],
            'cssfiles': [geturl(f) for f in cssfiles],
            'object': obj,
            'props': props,
            'opts': { k: v
                      for k, v in self.request.GET.items() },
            'embedurl': self.request.build_absolute_uri(),
            'randomness': utils.mkrandstr(),
        })
        return context
