from collections import defaultdict
from decimal import Decimal

from rest_framework.generics import ListAPIView
from django.views.decorators.http import require_GET
from django.db.models import CharField, Q
from django.db.models.expressions import F
from django.db.models.aggregates import Count, Sum
from django.db.models.functions import Length

from dv.lib.http import JsonResponse
from dv.models import (
    Allocation, BilateralInitiative, Indicator, NUTS, OrganisationRole,
    Programme, Project, State,
    DEFAULT_PERIOD, FUNDING_PERIODS_DICT, FINANCIAL_MECHANISMS_DICT, FM_EEA, FM_NORWAY,
)
from dv.serializers import ProjectSerializer
from dv.lib.utils import EEA_DONOR_STATES, DONOR_STATES_REVERSED

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
    ).order_by('short_name')
    programmes = defaultdict(list)
    for programme in programme_query:
        if programme.is_eea:
            if not programme.states.exists():
                programmes[(None, FM_EEA)].append(programme.short_name)
            for state in programme.states.all():
                programmes[(state.pk, FM_EEA)].append(programme.short_name)
        if programme.is_norway:
            if not programme.states.exists():
                programmes[(None, FM_NORWAY)].append(programme.short_name)
            for state in programme.states.all():
                programmes[(state.pk, FM_NORWAY)].append(programme.short_name)

    dpp_programme_query = programme_query.filter(
        organisation_roles__role_code='DPP',
    ).distinct()
    dpp_programmes = defaultdict(list)
    for programme in dpp_programme_query:
        if programme.is_eea:
            if not programme.states.exists():
                dpp_programmes[(None, FM_EEA)].append(programme.short_name)
            for state in programme.states.all():
                dpp_programmes[(state.pk, FM_EEA)].append(programme.short_name)
        if programme.is_norway:
            if not programme.states.exists():
                dpp_programmes[(None, FM_NORWAY)].append(programme.short_name)
            for state in programme.states.all():
                dpp_programmes[(state.pk, FM_NORWAY)].append(programme.short_name)

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

    out = []
    for allocation in allocations:
        state = allocation['state']
        financial_mechanism = allocation['financial_mechanism']
        out.append({
            'period': period,
            'fm': FINANCIAL_MECHANISMS_DICT[financial_mechanism],
            'beneficiary': state,
            'allocation': allocation['allocation'],
            'bilateral_fund': bilateral_fund.get((state, financial_mechanism), 0),
            "programmes": programmes.get((state, financial_mechanism), []),
            "DPP_programmes": dpp_programmes.get((state, financial_mechanism), []),
            "dpp_projects": dpp_projects.get((state, financial_mechanism), []),
            "continued_coop": continued_coop.get((state, financial_mechanism), []),
            "projects": projects.get((state, financial_mechanism), []),
            "bilateral_initiatives": bilateral_initiatives.get((state, financial_mechanism), []),
            "positive_fx": positive_fx.get((state, financial_mechanism), []),
        })
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
    )
    results = defaultdict(lambda: defaultdict(dict))
    programmes = defaultdict(dict)
    for indicator in indicators:
        if indicator.is_eea:
            results[(FM_EEA, indicator.state_id, indicator.programme_area_id)][indicator.header].update({
                indicator.indicator: {
                "achievement": indicator.achievement_eea,
            }})
            programmes[(FM_EEA, indicator.state_id, indicator.programme_area_id)].update({
                indicator.programme.short_name: {
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
                indicator.programme.short_name: {
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
        financial_mechanisms = []
        if project.is_eea:
            financial_mechanisms.append(FM_EEA)
        if project.is_norway:
            financial_mechanisms.append(FM_NORWAY)

        for financial_mechanism in financial_mechanisms:
            for programme_area in project.programme_areas.all():
                key = (financial_mechanism, project.state_id, programme_area.id)
                projects[key].append(project.code)

                programme = project.programme
                if not programmes[key][programme.short_name]:
                    programmes[key][programme.short_name] = {
                        'name': programme.name,
                        'url': programme.url,
                        'nuts': defaultdict(lambda: defaultdict(list)),
                    }
                programme_nuts = programmes[key][programme.short_name]['nuts'][project.nuts_code]
                programme_nuts['total'].append(project.code)
                if project.has_ended:
                    programme_nuts['ended'].append(project.code)
                if project.is_positive_fx:
                    programme_nuts['positive'].append(project.code)

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
            'news': [],  # TODO review news import
        })
    return JsonResponse(out)


@require_GET
def partners(request):
    out = []
    return JsonResponse(out)


def beneficiary_detail(request, beneficiary):
    return project_nuts(beneficiary, True)


def project_nuts(beneficiary, force_nuts3):
    """
    Returns NUTS3-level allocations for the given state.
    """
    try:
        state = State.objects.get_by_natural_key(beneficiary)
    except State.DoesNotExist:
        return JsonResponse({
            'error': "Beneficiary state '%s' does not exist." % beneficiary
        }, status=404)

    fields = {
        'id': F('nuts'),
        'area': F('programme_area__name'),
        'sector': F('programme_area__priority_sector__name'),
        'fm': F('programme_area__financial_mechanism__grant_name'),
    }
    select_fields = list(fields.keys()) + ['programme_id']
    data = (
        Project.objects.filter(state=state)
        .annotate(**fields)
        .values(*select_fields)
        .annotate(
            allocation=Sum('allocation'),
            project_count=Count('code'),
        )
    )

    # split all non-level3 allocation among level3s, but
    #
    # NOTE: "In every country at every NUTS level the “Extra-Regio” regions
    # have been designated (coded by adding to a two-letter country code
    # the letter Z at NUTS level 1, letters ZZ at NUTS level 2 and letters
    # ZZZ at NUTS level 3)."
    #
    # (we'll pretend the Zs are root)

    nuts3s = tuple(
        NUTS.objects
        .filter(code__startswith=beneficiary, code__length=5)
        .exclude(code__endswith="Z")  # skip extra-regio
        .order_by('code')
        .values_list('code', flat=True)
    )

    dataset = defaultdict(lambda: {
        'allocation': 0,
        'project_count': 0,
        'programmes': {},
    })

    for a in data:
        code = a['id']
        if len(code) > 2 and code.endswith('Z'):  # extra-regio
            code = code[:2]

        key = a['id'] + a['area'] + a['sector'] + a['fm']
        if not force_nuts3 or len(code) == 5:
            row = dataset[key]
            row['id'] = a['id']
            row['area'] = a['area']
            row['sector'] = a['sector']
            row['fm'] = a['fm']
            row['allocation'] += a['allocation']
            row['project_count'] += a['project_count']
            row['programmes'][a['programme_id']] = a['programme_id']
            continue

        # else split allocation among children, and add project count to all children
        children = (nuts3s if len(code) == 2
                    else [n for n in nuts3s if n.startswith(code)])

        if len(children) == 0:
            # TODO: this is an error. log it, etc.
            continue

        allocation = a['allocation'] / len(children)

        for nuts in children:
            childkey = nuts + a['area'] + a['sector'] + a['fm']
            row = dataset[childkey]
            row['id'] = nuts
            row['area'] = a['area']
            row['sector'] = a['sector']
            row['fm'] = a['fm']
            row['allocation'] += allocation
            row['programmes'][a['programme_id']] = a['programme_id']
            row['project_count'] += a['project_count']

    out = []

    for key, row in dataset.items():
        # strip away some of that crazy precision
        row['allocation'] = row['allocation'].quantize(Decimal('1.00'))
        out.append(row)

    return JsonResponse(out)


def projects_beneficiary_detail(request, beneficiary):
    return project_nuts(beneficiary, False)

#    # TODO: this copy-paste is evil. must ... fix ...
#    try:
#        state = State.objects.get_by_natural_key(beneficiary)
#    except State.DoesNotExist:
#        return JsonResponse({
#            'error': "Beneficiary state '%s' does not exist." % beneficiary
#        }, status=404)
#
#    fields = {
#        'id': F('nuts'),
#        'area': F('programme_area__name'),
#        'sector': F('programme_area__priority_sector__name'),
#        'fm': F('programme_area__financial_mechanism__grant_name'),
#    }
#    data = (
#        Project.objects.filter(state=state)
#        .filter(nuts__length__gt=2)
#        .exclude(nuts__endswith="Z")
#        .annotate(**fields)
#        .values(*fields.keys())
#        .annotate(
#            allocation=Sum('allocation'),
#            project_count=Count('code'),
#        )
#    )
#
#    out = list(data)
#
#    for row in out:
#        # strip away some of that crazy precision
#        row['allocation'] = row['allocation'].quantize(Decimal('1.00'))
#
#    return JsonResponse(out)


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
