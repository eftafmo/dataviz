import os.path
import re
from collections import defaultdict
from collections import OrderedDict

from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
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
    order_field = None
    template_name = 'search.html'
    paginate_by = 10
    context_object_name = 'object_list'

    def form_invalid(self, form):
        self.queryset = form.search()
        return super().form_invalid(form)

    def get_paginate_by(self, queryset):
        return self.request.GET.get('paginate_by', self.paginate_by)

    PRG_STATUS_SORT = {
        'Implementation': 0,
        'Closed': 1,
        'Approved': 2,
        'Withdrawn': 3,
        'Returned to po': 4,
    }
    PRJ_STATUS_SORT = {
        'In Progress': 0,
        'Completed': 1,
        'Non Completed': 2,
        'Terminated': 3,
    }
    AREAS_LIST = ProgrammeArea.objects.order_by(
        '-order'
    ).values(
        'name',
        'priority_sector__name',
        'priority_sector__type__grant_name',
        'order',
    )
    # sort by -order because there are some duplicated names and we need the first occurrence only
    AREAS_SORT = dict([(x['name'], x['order']) for x in AREAS_LIST])
    SECTORS_SORT = dict([(
        x['priority_sector__name'],
        x['order']
    ) for x in AREAS_LIST])

    # dicts for filter_facets
    AREAS_SECTORS = defaultdict(set)
    AREAS_FMS = defaultdict(set)
    SECTORS_FMS = defaultdict(set)
    for x in AREAS_LIST:
        AREAS_SECTORS[x['name']].add(x['priority_sector__name'])
        AREAS_FMS[x['name']].add(x['priority_sector__type__grant_name'])
        SECTORS_FMS[x['priority_sector__name']].add(x['priority_sector__type__grant_name'])

    ORG_ROLE_SORT = {
        'National Focal Point': 0,
        'Programme Operator': 1,
        'Donor Programme Partner': 2,
        'Project Promoter': 3,
        'Donor Project Partner': 4,
        'Programme Partner': 5,
        'Project Partner': 6,
    }

    # Donor states first (incl. France as International), then beneficiary states
    COUNTRY_SORT_BOOST = {
        'Iceland': 0,
        'Liechtenstein': 0,
        'Norway': 0,

        'France': 1,

        'Bulgaria': 2,
        'Cyprus': 2,
        'Czech Republic': 2,
        'Estonia': 2,
        'Greece': 2,
        'Hungary': 2,
        'Latvia': 2,
        'Lithuania': 2,
        'Malta': 2,
        'Poland': 2,
        'Portugal': 2,
        'Romania': 2,
        'Slovakia': 2,
        'Slovenia': 2,
        'Spain': 2,
        'Croatia': 2,
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
                    key=lambda x: order.get(x[0], 99)
                )
        # Special case for Country, refs #413
        if 'country' in facets:
            facets['country'] = sorted(
                facets['country'],
                key=lambda x: (self.COUNTRY_SORT_BOOST.get(x[0], 10) * 255 + ord(x[0][0]))
            )

    def filter_facets(self, facet_fields, form_facets):
        if form_facets['financial_mechanism_ss']:
            fms = set(form_facets['financial_mechanism_ss'])
            # Narrow sectors and programme areas
            facet_fields['priority_sector_ss'] = [(
                x[0], x[1]
            ) for x in facet_fields['priority_sector_ss']
                if len(self.SECTORS_FMS[x[0]] & fms)
            ]
            facet_fields['programme_area_ss'] = [(
                x[0], x[1]
            ) for x in facet_fields['programme_area_ss']
                if len(self.AREAS_FMS[x[0]] & fms)
            ]
        if form_facets['priority_sector_ss']:
            sectors = set(form_facets['priority_sector_ss'])
            facet_fields['programme_area_ss'] = [(
                x[0], x[1]
            ) for x in facet_fields['programme_area_ss']
                if len(self.AREAS_SECTORS[x[0]] & sectors)
            ]
            # also filter fm facet if sector is selected
            fms = [fm for x in sectors for fm in self.SECTORS_FMS[x]]
            facet_fields['financial_mechanism_ss'] = [(
                x[0], x[1]
            ) for x in facet_fields['financial_mechanism_ss']
                if x[0] in fms
            ]
        if form_facets['programme_area_ss']:
            areas = set(form_facets['programme_area_ss'])
            fms = [fm for x in areas for fm in self.AREAS_FMS[x]]
            sectors = [ps for x in areas for ps in self.AREAS_SECTORS[x]]
            facet_fields['financial_mechanism_ss'] = [(
                x[0], x[1]
            ) for x in facet_fields['financial_mechanism_ss']
                if x[0] in fms
            ]
            facet_fields['priority_sector_ss'] = [(
                x[0], x[1]
            ) for x in facet_fields['priority_sector_ss']
                if x[0] in sectors
            ]

        # Note: outcomes are still not filtered by FM
        # see programme PL04, outcome PA4101

    def get_context_data(self, *args, **kwargs):
        objls = kwargs.pop('object_list', self.queryset)
        ctx = super().get_context_data(object_list=objls, **kwargs)
        ctx['page_sizes'] = [10, 25, 50, 100]

        facet_fields = ctx.get('facets', {}).get('fields', {})
        # Custom sorting of some facets, refs #326
        self.reorder_facets(facet_fields)
        # Custom filtering of PS/PA facets, refs #329
        self.filter_facets(facet_fields, kwargs['form'].facets)

        return ctx

    def get_queryset(self):
        # Override default Solr settings
        qs = super(BaseFacetedSearchMixin, self).get_queryset()
        for field in self.facet_fields:
            qs = qs.facet(field, mincount=1, limit=10000, sort='index')
        if self.order_field:
            qs = qs.order_by(self.order_field)
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
    order_field = 'code'

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
    order_field = 'code'


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
    order_field = '-role_max_priority_code'

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
                if org_role.programme and org_role.programme.is_tap:
                    continue
                prg_or_prj = org_role.programme
                if org_role.project:
                    prg_or_prj = org_role.project
                if prg_or_prj:
                    d[role_name].append({
                        'name': '{} - {}'.format(prg_or_prj.code, prg_or_prj.name),
                        'url': prg_or_prj.url,
                    })
            for role, plist in d.items():
                # Sort programmes and projects
                d[role] = sorted(plist, key=lambda p: p['name'])
            # Sort by role name
            res.prep_roles = OrderedDict(
                sorted(
                    d.items(), key=lambda item: self.ORG_ROLE_SORT.get(item[0], 99)
                )
            )
        return ctx


class NewsFacetedSearchView(FacetedSearchView):
    facet_fields = ProjectFacetedSearchView.facet_fields
    order_field = '-created_dt'

    initial = {
        'kind': ['News'],
        # hack! we remove this at form init
        'view_name': 'NewsFacetedSearchView'
    }


class _TypeaheadFacetedSearchView:
    form_class = EeaAutoFacetedSearchForm
    template_name = None
    results_limit = 10

    def get_data(self, context):
        form = context['form']
        facets = context['facets']['fields'][form.auto_name]
        # facets format: [(value, count), ...]
        facets.sort(
            key=lambda facet: facet[1],
            reverse=True
        )

        paginator = Paginator(facets, self.results_limit)
        page = self.request.GET.get('page', 1)
        try:
            facets = paginator.page(page)
        except PageNotAnInteger or EmptyPage:
            page = 1
            facets = paginator.page(1)

        return {
            'results': [
                {'text': facet, 'id': facet}
                for facet, count in facets
            ],
            'results_for': form.auto_name,
            'total_count': paginator.count,
            'page': page,
            'pagination': {'more': int(page) < paginator.num_pages}
        }

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(self.get_data(context), **response_kwargs)


class ProjectTypeaheadFacetedSearchView(_TypeaheadFacetedSearchView,
                                        ProjectFacetedSearchView):
    pass


class OrganisationTypeaheadFacetedSearchView(_TypeaheadFacetedSearchView,
                                             OrganisationFacetedSearchView):
    pass


class NewsTypeaheadFacetedSearchView(_TypeaheadFacetedSearchView,
                                     NewsFacetedSearchView):
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


        jsfiles = webpack.get_files('common', 'js') + webpack.get_files('dataviz', 'js')
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
        if scenario in ("grants", "projects") and component == "xmap":
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
