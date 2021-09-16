import html
from collections import defaultdict
from decimal import Decimal
from itertools import product

from rest_framework.generics import ListAPIView
from django.views.decorators.http import require_GET
from django.db.models import CharField, Q
from django.db.models.expressions import F
from django.db.models.aggregates import Count, Sum
from django.db.models.functions import Length

from dv.lib.http import JsonResponse
from dv.models import (
    Allocation, BilateralInitiative, Indicator, News, NUTS, OrganisationRole,
    Programme, ProgrammeAllocation, Project, State,
    DEFAULT_PERIOD, FUNDING_PERIODS_DICT, FINANCIAL_MECHANISMS_DICT, FM_EEA, FM_NORWAY,
)
from dv.serializers import ProjectSerializer
from dv.lib.utils import DONOR_STATES, EEA_DONOR_STATES, DONOR_STATES_REVERSED

CharField.register_lookup(Length, 'length')


def test_sentry(request):
    raise Exception('Testing sentry...')


@require_GET
def overview(request):
    period = request.GET.get('period', DEFAULT_PERIOD)  # used in FE
    period_id = FUNDING_PERIODS_DICT[period]  # used in queries

    allocations = Allocation.objects.filter(
        funding_period=period_id,
    ).values(
        'financial_mechanism',
        'state'
    ).annotate(
        allocation=Sum('gross_allocation')
    ).order_by('state', 'financial_mechanism')

    bilateral_fund = {
        (bf['state'], bf['financial_mechanism']): bf['allocation']
        for bf in allocations.filter(programme_area__code='OTBF')
    }

    programme_query = Programme.objects.filter(
        funding_period=period_id,
        is_tap=False,
        is_bfp=False,
    ).order_by('code')
    programmes = defaultdict(list)
    for programme in programme_query:
        if programme.is_eea:
            if not programme.states.exists():
                programmes[(None, FM_EEA)].append(programme.code)
            for state in programme.states.all():
                programmes[(state.pk, FM_EEA)].append(programme.code)
        if programme.is_norway:
            if not programme.states.exists():
                programmes[(None, FM_NORWAY)].append(programme.code)
            for state in programme.states.all():
                programmes[(state.pk, FM_NORWAY)].append(programme.code)

    dpp_programme_query = programme_query.filter(
        organisation_roles__role_code='DPP',
    ).distinct()
    dpp_programmes = defaultdict(list)
    for programme in dpp_programme_query:
        if programme.is_eea:
            if not programme.states.exists():
                dpp_programmes[(None, FM_EEA)].append(programme.code)
            for state in programme.states.all():
                dpp_programmes[(state.pk, FM_EEA)].append(programme.code)
        if programme.is_norway:
            if not programme.states.exists():
                dpp_programmes[(None, FM_NORWAY)].append(programme.code)
            for state in programme.states.all():
                dpp_programmes[(state.pk, FM_NORWAY)].append(programme.code)

    project_query = Project.objects.filter(
        funding_period=period_id,
    ).values(
        'code',
        'is_eea',
        'is_norway',
        'is_dpp',
        'is_continued_coop',
        'is_positive_fx',
        'state',
    ).order_by('code')
    projects = defaultdict(list)
    dpp_projects = defaultdict(list)
    continued_coop = defaultdict(list)
    positive_fx = defaultdict(list)
    for project in project_query:
        if project['is_eea']:
            projects[(project['state'], FM_EEA)].append(project['code'])
            if project['is_dpp']:
                dpp_projects[(project['state'], FM_EEA)].append(project['code'])
            if project['is_continued_coop']:
                continued_coop[(project['state'], FM_EEA)].append(project['code'])
            if project['is_positive_fx']:
                positive_fx[(project['state'], FM_EEA)].append(project['code'])
        if project['is_norway']:
            projects[(project['state'], FM_NORWAY)].append(project['code'])
            if project['is_dpp']:
                dpp_projects[(project['state'], FM_NORWAY)].append(project['code'])
            if project['is_continued_coop']:
                continued_coop[(project['state'], FM_NORWAY)].append(project['code'])
            if project['is_positive_fx']:
                positive_fx[(project['state'], FM_NORWAY)].append(project['code'])

    bilateral_initiative_query = BilateralInitiative.objects.filter(
        funding_period=period_id,
    ).select_related(
        'programme',
    )
    bilateral_initiatives = defaultdict(list)
    # TODO is it ok to decide if BI is EEA/Norway based on programme?
    for bi in bilateral_initiative_query:
        if bi.programme.is_eea:
            bilateral_initiatives[(bi.state.pk, FM_EEA)].append(bi.code)
        if bi.programme.is_norway:
            bilateral_initiatives[(bi.state.pk, FM_NORWAY)].append(bi.code)

    RELEVANT_INDICATORS = {
        'Number of people engaged in civil society organisation activities': 'people_civil_society',
        'Estimated annual CO2 emissions reductions': 'co2_emissions_reduction',
        'Number of researchers supported': 'supported_researchers',
        'Number of professional staff trained': 'staff_trained',
        'Number of jobs created': 'jobs_created',
    }
    indicator_query = Indicator.objects.filter(
        Q(achievement_eea__gt=0) | Q(achievement_norway__gt=0),
        funding_period=period_id,
        indicator__in=RELEVANT_INDICATORS.keys(),
    )
    indicators = defaultdict(lambda: defaultdict(int))
    for indicator in indicator_query:
        key = indicators[RELEVANT_INDICATORS[indicator.indicator]]
        if indicator.achievement_eea:
            key[(indicator.state_id, FM_EEA)] += indicator.achievement_eea
        if indicator.achievement_norway:
            key[(indicator.state_id, FM_NORWAY)] += indicator.achievement_norway

    out = []
    for allocation in allocations:
        state = allocation['state']
        financial_mechanism = allocation['financial_mechanism']
        key = (state, financial_mechanism)
        element = {
            'period': period,
            'fm': FINANCIAL_MECHANISMS_DICT[financial_mechanism],
            'beneficiary': state,
            'allocation': allocation['allocation'],
            'bilateral_fund': bilateral_fund.get(key, 0),
            'programmes': programmes.get(key, []),
            'DPP_programmes': dpp_programmes.get(key, []),
            'dpp_projects': dpp_projects.get(key, []),
            'continued_coop': continued_coop.get(key, []),
            'projects': projects.get(key, []),
            'bilateral_initiatives': bilateral_initiatives.get(key, []),
            'positive_fx': positive_fx.get(key, []),
        }
        for indicator in RELEVANT_INDICATORS.values():
            element[indicator] = indicators[indicator].get(key, 0)
        out.append(element)
    return JsonResponse(out)


@require_GET
def grants(request):
    period = request.GET.get('period', DEFAULT_PERIOD)  # used in FE
    period_id = FUNDING_PERIODS_DICT[period]  # used in queries

    allocations = Allocation.objects.filter(
        funding_period=period_id,
        programme_area__isnull=False,
    ).exclude(
        gross_allocation=0,  # TODO should we still exclude this?
    ).select_related(
        'programme_area',
        'programme_area__priority_sector',
    ).order_by('state', 'financial_mechanism')

    bilateral_fund = {
        (bf.financial_mechanism, bf.state_id, bf.programme_area_id): bf.gross_allocation
        for bf in allocations.filter(programme_area__code='OTBF')
    }

    indicators = Indicator.objects.filter(
        funding_period=period_id,
        programme__is_tap=False,
    ).select_related(
        'programme',
    ).order_by(F('order').asc(nulls_last=True))

    results = defaultdict(lambda: defaultdict(dict))
    programmes = defaultdict(dict)
    for indicator in indicators:
        if indicator.is_eea:
            results[(FM_EEA, indicator.state_id, indicator.programme_area_id)][indicator.header].update({
                indicator.indicator: {
                "achievement": indicator.achievement_eea,
            }})
            programmes[(FM_EEA, indicator.state_id, indicator.programme_area_id)].update({
                indicator.programme.code: {
                    'name': indicator.programme.name,
                    'url': indicator.programme.url,
                }
            })
        if indicator.is_norway:
            results[(FM_NORWAY, indicator.state_id, indicator.programme_area_id)][indicator.header].update({
                indicator.indicator: {
                "achievement": indicator.achievement_norway,
            }})
            programmes[(FM_NORWAY, indicator.state_id, indicator.programme_area_id)].update({
                indicator.programme.code: {
                    'name': indicator.programme.name,
                    'url': indicator.programme.url,
                }
            })


    out = []
    for allocation in allocations:
        state = allocation.state_id
        financial_mechanism = allocation.financial_mechanism
        programme_area = allocation.programme_area_id
        out.append({
            'period': period,
            'fm': FINANCIAL_MECHANISMS_DICT[financial_mechanism],
            'sector': allocation.programme_area.priority_sector.name,
            'area': allocation.programme_area.name,
            'beneficiary': state,
            'is_ta': allocation.programme_area.priority_sector.code == 'OT',
            'allocation': allocation.gross_allocation,
            'net_allocation': allocation.net_allocation,
            'bilateral_allocation': bilateral_fund.get((financial_mechanism, state, programme_area), 0),  # TODO this doesn't look right
            'results': results[(financial_mechanism, state, programme_area)],
            'programmes': programmes[(financial_mechanism, state, programme_area)],
            'thematic': allocation.thematic,
        })

    return JsonResponse(out)


@require_GET
def projects(request):
    period = request.GET.get('period', DEFAULT_PERIOD)  # used in FE
    period_id = FUNDING_PERIODS_DICT[period]  # used in queries

    allocations = Allocation.objects.filter(
        funding_period=period_id,
        programme_area__isnull=False,
    ).exclude(
        gross_allocation=0,
    ).select_related(
        'programme_area',
        'programme_area__priority_sector',
    ).order_by('state', 'financial_mechanism')

    project_query = Project.objects.filter(
        funding_period=period_id,
    ).select_related(
        'programme',
    ).prefetch_related(
        'programme_areas',
    )

    programmes = defaultdict(lambda: defaultdict(dict))
    projects = defaultdict(list)
    for project in project_query:
        for financial_mechanism in project.financial_mechanisms:
            for programme_area in project.programme_areas.all():
                key = (financial_mechanism, project.state_id, programme_area.id)
                projects[key].append(project.code)

                programme = project.programme
                if not programmes[key][programme.code]:
                    programmes[key][programme.code] = {
                        'name': programme.name,
                        'url': programme.url,
                        'nuts': defaultdict(lambda: defaultdict(list)),
                    }
                programme_nuts = programmes[key][programme.code]['nuts'][project.nuts_id]
                programme_nuts['total'].append(project.code)
                if project.has_ended:
                    programme_nuts['ended'].append(project.code)
                if project.is_positive_fx:
                    programme_nuts['positive'].append(project.code)

    news_query = News.objects.filter(
            project__funding_period=period_id,
        ).exclude(project_id__isnull=True
        ).select_related(
            'project',
        ).prefetch_related(
            'project__programme_areas',
        ).order_by('-created')
    news = defaultdict(list)
    for item in news_query:
        keys = product(
            item.project.financial_mechanisms,
            (item.project.state_id, ),
            item.project.programme_areas.values_list('id', flat=True),
        )
        for key in keys:
            news[key].append({
                'title': html.unescape(item.title or ''),
                'link': item.link,
                'created': item.created,
                'summary': item.summary,
                'image': item.image,
                'nuts': item.project.nuts_id,
            })

    out = []
    for allocation in allocations:
        state = allocation.state_id
        financial_mechanism = allocation.financial_mechanism
        programme_area = allocation.programme_area_id
        key = (financial_mechanism, state, programme_area)
        out.append({
            'period': period,
            'fm': FINANCIAL_MECHANISMS_DICT[financial_mechanism],
            'sector': allocation.programme_area.priority_sector.name,
            'area': allocation.programme_area.name,
            'beneficiary': state,
            'is_ta': allocation.programme_area.priority_sector.code == 'OT',
            'allocation': allocation.gross_allocation,
            'net_allocation': allocation.net_allocation,
            'programmes': programmes[key],
            'projects': projects[key],
            'project_allocation': 0,  # TODO get project allocation split between the two FMs
            'news': news[key],
        })
    return JsonResponse(out)


@require_GET
def partners(request):
    # List of programmes having DPP or dpp
    # Everything else will be grouped by these
    partnership_programmes_query = ProgrammeAllocation.objects.filter(
        programme__organisation_roles__role_code__in=('DPP', 'PJDPP')
    ).select_related(
        'programme_area',
        'priority_sector',
        'programme'
    )

    partnership_programmes = {}
    # Compute allocations per Programme and Programme area
    allocations = defaultdict(int)
    for p in partnership_programmes_query:
        if p.programme.code not in partnership_programmes:
            partnership_programmes[p.programme.code] = {
                'name': p.programme.name,
                'url': p.programme.url,
                'areas': {},
                'beneficiaries': set(),
                'donors': set(),
                'DPP': {},
                'PO': {},
                'news': [],
                'allocation': 0,
            }
        partnership_programmes[p.programme.code]['allocation'] += p.allocation
        partnership_programmes[p.programme.code]['beneficiaries'].add(p.state_id)
        if p.programme_area:
            partnership_programmes[p.programme.code]['areas'][p.programme_area.code] = {
                'area': p.programme_area.name,
                'sector': p.priority_sector.name,
                'fm': FINANCIAL_MECHANISMS_DICT[p.financial_mechanism],
            }
        key = (
            p.programme.code,
            p.programme_area.code if p.programme_area else None,
            p.state_id,
        )
        allocations[key] += p.allocation

    partnership_programmes_ids = partnership_programmes.keys()

    # Get donor countries for each programme
    programme_donors_query = OrganisationRole.objects.values(
        'programme_id',
        'organisation_country',
    ).exclude(
        programme_id__isnull=True,
    ).filter(
        role_code__in=('DPP', 'PJDPP'),
    ).distinct()

    for p in programme_donors_query:
        partnership_programmes[p['programme_id']]['donors'].add(
            DONOR_STATES.get(p['organisation_country'], 'Intl')
        )

    # Get programme partners (DPP and PO)
    programme_partners_query = OrganisationRole.objects.filter(
        programme_id__in=partnership_programmes_ids,
        role_code__in=('DPP', 'PO'),
    ).annotate(
        org_id=F('organisation_id'),
        name=F('organisation_name'),
        country=F('organisation_country'),
        role=F('role_code'),
        nuts=F('nuts_code'),
    ).values(
        'country',
        'org_id',
        'name',
        'programme_id',
        'role',
        'nuts',
    ).order_by('role_code').distinct()
    # Order by - for filtering out PO when no DPP is present

    donor_programme_partners = defaultdict(dict)
    donor_programmes = set()
    # Donor programmes = only those having a DPP
    for pp in programme_partners_query:
        programme_code = pp['programme_id']
        if pp['role'] == 'DPP':
            donor = DONOR_STATES.get(pp['country'], 'Intl')
            key = (programme_code, donor)
            donor_programme_partners[key][pp['org_id']] = {
                'name': pp['name'],
                'nuts': pp['nuts'],
            }
            donor_programmes.add(programme_code)
        elif programme_code in donor_programmes:
            partnership_programmes[programme_code]['PO'][pp['org_id']] = {
                'name': pp['name'],
                'nuts': pp['nuts'],
            }

    # Get project partners (dpp and project promoters)
    project_partners_query = OrganisationRole.objects.select_related(
        'project',
    ).filter(
        programme_id__in=partnership_programmes_ids,
        role_code__in=('PJDPP', 'PJPT'),
    ).values(
        'organisation_id',
        'organisation_name',
        'organisation_country',
        'role_code',
        'nuts_code',
        'project_id',
        'programme_id',
        'project__state_id',
        'project__is_dpp',
        'project__has_ended',
        'project__is_continued_coop',
        'project__is_improved_knowledge',
    ).prefetch_related(
        'project__programme_areas',
    ).order_by('role_code').distinct()
    # Order by - for filtering out project promoters when no PJDPP is present

    projects, project_promoters, donor_project_partners = (
        defaultdict(dict), defaultdict(dict), defaultdict(dict)
    )
    donor_projects = set()
    project_nuts = {}

    for pp in project_partners_query:
        # Projects have only one BS and one PA, so keep them separated
        pass
        # TODO WIP

    out = []
    return JsonResponse(out)


def beneficiary_detail(request, beneficiary):
    return project_nuts(beneficiary, True)


def project_nuts(beneficiary, force_nuts3):
    """
    Returns NUTS3-level allocations for the given state.
    """
    out = []
    return JsonResponse(out)


def projects_beneficiary_detail(request, beneficiary):
    return project_nuts(beneficiary, False)


class ProjectList(ListAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        programme = self.request.query_params.get('programme', None)
        queryset = Project.objects.all()

        if programme is not None:
            queryset = queryset.filter(programme_id=programme)

        beneficiary = self.request.query_params.get('beneficiary', None)
        if beneficiary is not None:
            queryset = queryset.filter(state_id=beneficiary)

        fm_name = self.request.query_params.get('fm', None)
        if fm_name:
            queryset = queryset.filter(financial_mechanism__grant_name=fm_name)

        programme_area_name = self.request.query_params.get('area', None)
        if programme_area_name:
            queryset = queryset.filter(programme_area__name=programme_area_name)
        else:
            # Don't add sector name if programme area is present
            sector_name = self.request.query_params.get('sector', None)
            if sector_name:
                queryset = queryset.filter(programme_area__priority_sector__name=sector_name)

        nuts = self.request.query_params.get('nuts', None)
        if nuts:
            queryset = queryset.filter(nuts__startswith=nuts)

        is_dpp = self.request.query_params.get('is_dpp', None)
        if is_dpp:
            queryset = queryset.filter(is_dpp=True)

        donor = self.request.query_params.get('donor', None)
        if is_dpp and donor:
            donor_name = DONOR_STATES_REVERSED.get(donor)

            q = Q(organisation_roles__organisation_role_id='PJDPP')
            if donor_name:
                q = q & Q(organisation_roles__organisation__country=donor_name)
            else:
                q = q & ~Q(organisation_roles__organisation__country__in=EEA_DONOR_STATES.keys())
                # Django ORM generates an unnecessary complicated query here
            queryset = queryset.filter(q)
        return queryset.order_by('code').distinct()
