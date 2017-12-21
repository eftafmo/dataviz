import io
import os.path
import re
from collections import defaultdict
from collections import OrderedDict
from datetime import datetime

from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from haystack.generic_views import FacetedSearchView as BaseFacetedSearchView
from haystack.generic_views import FacetedSearchMixin as BaseFacetedSearchMixin
from pyexcel import Sheet
from webpack_loader import utils as webpack
from dv.lib import utils
from dv.models import (
    StaticContent,
    ProgrammeArea,
    State,
)
from dv.views.facets_rules import (
    BASE_FACETS, PROGRAMME_FACETS, PROJECT_FACETS,
    ORGANISATION_FACETS, NEWS_FACETS,
    FACET_MIN_COUNT, FACET_LIMIT, FACET_SORT,
    COUNTRY_SORT_BOOST, ORG_ROLE_SORT,
    ModelFacetRules,
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
    facet_rules = OrderedDict(BASE_FACETS)
    facet_kind = None
    order_field = None
    template_name = 'search/main.html'
    paginate_by = 10
    context_object_name = 'object_list'

    def __init__(self):
        super().__init__()
        self.facet_fields = self.facet_rules.keys()
        ModelFacetRules.init_reordering_rules()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'facet_rules': self.facet_rules,
            'facet_kind': self.facet_kind,
        })
        return kwargs

    def form_invalid(self, form):
        self.queryset = form.search()
        return super().form_invalid(form)

    def get_paginate_by(self, queryset):
        return self.request.GET.get('paginate_by', self.paginate_by)

    def reorder_facets(self, facets):
        for facet, order in ModelFacetRules.REORDER_FACETS.items():
            if facet in facets:
                facets[facet] = sorted(
                    facets[facet],
                    key=lambda x: order.get(x[0], 99)
                )
        # Special case for Country, refs #413
        if 'country' in facets:
            facets['country'] = sorted(
                facets['country'],
                key=lambda x: (COUNTRY_SORT_BOOST.get(x[0], 10) * 255 + ord(x[0][0]))
            )

    def filter_facets(self, facet_fields, form_facets):
        if form_facets['financial_mechanism_ss']:
            fms = set(form_facets['financial_mechanism_ss'])
            # Narrow sectors and programme areas
            facet_fields['priority_sector_ss'] = [(
                x[0], x[1]
            ) for x in facet_fields['priority_sector_ss']
                if len(ModelFacetRules.SECTORS_FMS[x[0]] & fms)
            ]
            facet_fields['programme_area_ss'] = [(
                x[0], x[1]
            ) for x in facet_fields['programme_area_ss']
                if len(ModelFacetRules.AREAS_FMS[x[0]] & fms)
            ]
        if form_facets['priority_sector_ss']:
            sectors = set(form_facets['priority_sector_ss'])
            facet_fields['programme_area_ss'] = [(
                x[0], x[1]
            ) for x in facet_fields['programme_area_ss']
                if len(ModelFacetRules.AREAS_SECTORS[x[0]] & sectors)
            ]
            # also filter fm facet if sector is selected
            fms = [fm for x in sectors for fm in ModelFacetRules.SECTORS_FMS[x]]
            facet_fields['financial_mechanism_ss'] = [(
                x[0], x[1]
            ) for x in facet_fields['financial_mechanism_ss']
                if x[0] in fms
            ]
        if form_facets['programme_area_ss']:
            areas = set(form_facets['programme_area_ss'])
            fms = [fm for x in areas for fm in ModelFacetRules.AREAS_FMS[x]]
            sectors = [ps for x in areas for ps in ModelFacetRules.AREAS_SECTORS[x]]
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

        ctx['query'] = [
            (key, value)
            for key in self.request.GET.keys()
            for value in self.request.GET.getlist(key)
        ]
        ctx['kind'] = self.facet_kind
        ctx['facet_rules'] = self.facet_rules

        facet_fields = self.queryset.facet_counts()['fields']
        # Custom sorting of some facets, refs #326
        self.reorder_facets(facet_fields)
        # Custom filtering of PS/PA facets, refs #329
        self.filter_facets(facet_fields, kwargs['form'].facets)

        return ctx

    def get_queryset(self):
        # Override default Solr settings
        qs = super(BaseFacetedSearchMixin, self).get_queryset()
        for field in self.facet_fields:
            qs = qs.facet(
                field,
                mincount=FACET_MIN_COUNT,
                limit=FACET_LIMIT,
                sort=FACET_SORT
            )
        if self.order_field:
            qs = qs.order_by(self.order_field)
        return qs


class ProgrammeFacetedSearchView(FacetedSearchView):
    facet_rules = PROGRAMME_FACETS
    facet_kind = 'Programme'
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
    facet_rules = PROJECT_FACETS
    facet_kind = 'Project'
    order_field = 'code'


class OrganisationFacetedSearchView(FacetedSearchView):
    facet_rules = ORGANISATION_FACETS
    facet_kind = 'Organisation'
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
        # states.extend(['Liechtenstein', 'Norway', 'Iceland'])
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
                    d.items(), key=lambda item: ORG_ROLE_SORT.get(item[0], 99)
                )
            )
        return ctx


class NewsFacetedSearchView(FacetedSearchView):
    facet_rules = NEWS_FACETS
    facet_kind = 'News'
    order_field = '-created_dt'


class FacetedExportView(FacetedSearchView):
    export_fields = {}

    def type_format_field(self, raw_value):
        if not raw_value:
            return ''
        if isinstance(raw_value, datetime):
            return raw_value.strftime("%d %B %Y")
        try:
            return float(raw_value)
        except ValueError:
            pass
        return raw_value

    def format_field(self, raw_field):
        if isinstance(raw_field, list):
            return '\n'.join([self.type_format_field(item) for item in raw_field])
        return self.type_format_field(raw_field)

    def get_export_data(self, form):
        queryset = form.search()
        result = queryset.values_list(*self.export_fields.keys())
        for row in result:
            for i in range(len(row)):
                row[i] = self.format_field(row[i])
        return result

    def get_paginate_by(self, queryset):
        return queryset.count()

    def form_valid(self, form):
        data = self.get_export_data(form)
        name = self.facet_kind
        sheet = Sheet(data,
                      name=name,
                      colnames=list(self.export_fields.values()))
        stream = io.BytesIO()
        stream = sheet.save_to_memory('xlsx', stream)
        response = HttpResponse(stream.read())
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response['Content-Disposition'] = 'attachment; filename="{0}.xlsx"'.format(name)
        return response


class ProgrammeFacetedExportView(FacetedExportView):
    export_fields = OrderedDict([
        ('code', 'Case number'),
        ('name', 'Programme name'),
        ('financial_mechanism_ss', 'Financial mechanism'),
        ('priority_sector_ss', 'Sector'),
        ('programme_area_ss', 'Programme area'),
        ('state_name', 'Beneficiary state'),
        ('programme_status', 'Programme status'),
        ('grant', 'Grant'),
        ('outcome_ss', 'Outcome'),
        ('url', 'Url'),
    ])
    facet_kind = 'Programme'
    facet_rules = PROGRAMME_FACETS
    order_field = ProgrammeFacetedSearchView.order_field


class ProjectFacetedExportView(FacetedExportView):
    export_fields = OrderedDict({
        'code': 'Case number',
        'name': 'Project name',
        'financial_mechanism_ss': 'Financial mechanism',
        'priority_sector_ss': 'Sector',
        'programme_area_ss': 'Programme area',
        'state_name': 'Beneficiary state',
        'programme_status': 'Programme status',
        'project_status': 'Project status',
        'grant': 'Grant',
        'outcome_ss': 'Outcome',
        'geotarget': 'Project region or city',
        'theme_ss': 'Project theme',
        'url': 'Url'
    })
    facet_kind = 'Project'
    facet_rules = PROJECT_FACETS
    order_field = ProjectFacetedSearchView.order_field


class OrganisationFacetedExportView(FacetedExportView):
    export_fields = OrderedDict([
        ('name', 'Name'),
        ('domestic_name', 'Domestic name'),
        ('country', 'Country'),
        ('city', 'City'),
        ('role_ss', 'Organisation role'),
        ('org_type_category', 'Organisation category'),
        ('org_type', 'Organisation sub category'),
        ('financial_mechanism_ss', 'Financial mechanism'),
        ('priority_sector_ss', 'Sector'),
        ('programme_area_ss', 'Programme area'),
        ('state_name', 'Beneficiary state'),
        ('programme_status', 'Programme status'),
        ('project_name', 'Project name'),
        ('project_status', 'Project status'),
    ])
    facet_kind = 'Organisation'
    facet_rules = ORGANISATION_FACETS
    order_field = OrganisationFacetedSearchView.order_field


class NewsFacetedExportView(FacetedExportView):
    export_fields = OrderedDict([
        ('name', 'Title'),
        ('created_dt', 'Date'),
        ('financial_mechanism_ss', 'Financial mechanism'),
        ('priority_sector_ss', 'Sector'),
        ('programme_area_ss', 'Programme area'),
        ('state_name', 'Beneficiary state'),
        ('programme_name', 'Programme'),
        ('programme_status', 'Programme status'),
        ('project_name', 'Project'),
        ('project_status', 'Project status'),
        ('theme_ss', 'Project theme'),
        ('geotarget', 'Project region or city'),
        ('url', 'Url'),
    ])
    facet_kind = 'News'
    facet_rules = NEWS_FACETS
    order_field = NewsFacetedSearchView.order_field


class _TypeaheadFacetedSearchView(object):
    form_class = EeaAutoFacetedSearchForm
    template_name = None
    results_limit = 10

    def get_context_data(self, *args, **kwargs):
        # override so that it won't paginate queryset
        return {'form': kwargs['form']}

    def get_data(self, context):
        form = context['form']
        facets = self.queryset.facet_counts()['fields'][form.auto_name]
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
                {
                    'id': facet,
                    'text': "{0} ({1})".format(facet, count)
                }
                for facet, count in facets
            ],
            'results_for': form.auto_name,
            'total_count': paginator.count,
            'page': page,
            'pagination': {'more': int(page) < paginator.num_pages}
        }

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(self.get_data(context), **response_kwargs)


class ProgrammeTypeaheadFacetedSearchView(_TypeaheadFacetedSearchView,
                                          ProgrammeFacetedSearchView):
    pass


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


        jsfiles = webpack.get_files('dataviz', 'js')
        cssfiles = webpack.get_files('dataviz', 'css')

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
        elif scenario in ("partners", "projects") and component == "projects":
            props['detailsDatasource'] = self.request.build_absolute_uri(
                reverse("api:project-list")
            )
        elif scenario in ("partners", "projects") and component == "sidebar":
            props['projectsDatasource'] = self.request.build_absolute_uri(
                reverse("api:project-list")
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


class RobotsView(View):

    def get(self, request, *args, **kwargs):
        test_settings = [
            'Disallow: /',
        ]

        prod_settings = [
            'User-agent: *',
            'Crawl-delay: 10',
            'Disallow: /assets/',
            'Disallow: /api/',
            'Disallow: /embed/',
        ]

        if settings.DEBUG:
            robots = "\n".join(test_settings)
        else:
            robots = "\n".join(prod_settings)

        return HttpResponse(robots,
                            content_type='text/plain; charset=utf8')
