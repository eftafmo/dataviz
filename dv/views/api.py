import html
import re
from collections import defaultdict
from decimal import Decimal

from rest_framework.generics import ListAPIView
from django.views.decorators.http import require_GET
from django.db.models import CharField, Q
from django.db.models.expressions import F
from django.db.models.aggregates import Count, Sum
from django.db.models.functions import Length

from dv.lib.http import JsonResponse
from dv.models import Allocation, State, Programme, Project, NUTS
from dv.models import FUNDING_PERIODS_DICT, FINANCIAL_MECHANISMS_DICT, FM_EEA, FM_NORWAY
from dv.serializers import ProjectSerializer
from dv.lib.utils import EEA_DONOR_STATES, DONOR_STATES, DONOR_STATES_REVERSED

CharField.register_lookup(Length, 'length')


def test_sentry(request):
    division_by_zero = 1 / 0


@require_GET
def overview(request):
    # TODO see if FE will send value in db (3) or human-readable value (2014-2021)
    period = request.GET.get('period', 3)
    allocations = Allocation.objects.filter(
        funding_period=period,
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
        funding_period=period,
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

    project_query = Project.objects.filter(
        funding_period=period
    ).values(
        'code',
        'is_eea',
        'is_norway',
        'state',
    ).order_by('code')
    projects = defaultdict(list)
    for project in project_query:
        if project['is_eea']:
            projects[(project['state'], FM_EEA)].append(project['code'])
        if project['is_norway']:
            projects[(project['state'], FM_NORWAY)].append(project['code'])

    out = []
    for allocation in allocations:
        state = allocation['state']
        financial_mechanism = allocation['financial_mechanism']
        out.append({
            'period': FUNDING_PERIODS_DICT[period],
            'fm': FINANCIAL_MECHANISMS_DICT[financial_mechanism],
            'beneficiary': state,
            'allocation': allocation['allocation'],
            'bilateral_fund': bilateral_fund.get((state, financial_mechanism), 0),
            "programmes": programmes.get((state, financial_mechanism), []),
            "DPP_programmes": (),
            "dpp_projects": (),
            "continued_coop": (),
            "projects": projects.get((state, financial_mechanism), []),
            "bilateral_initiatives": (),
            "positive": (),
        })
    return JsonResponse(out)


@require_GET
def grants(request):
    out = []
    return JsonResponse(out)


@require_GET
def projects(request):
    out = []
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
