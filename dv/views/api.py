import html
import re
from collections import defaultdict
from decimal import Decimal
from itertools import chain, product

from django.views.decorators.http import require_GET
from django.db.models import CharField, Q
from django.db.models.expressions import F
from django.db.models.aggregates import Sum
from django.db.models.functions import Length
from rest_framework.generics import ListAPIView

from dv.lib.http import JsonResponse, SetEncoder
from dv.lib.utils import (
    DONOR_STATES, EEA_DONOR_STATES, DONOR_STATES_REVERSED, DEFAULT_PERIOD,
    FUNDING_PERIODS_DICT, FM_DICT, FM_REVERSED_DICT, FM_EEA, FM_NORWAY,
    NUTS_VERSION_BY_PERIOD, OVERVIEW_INDICATORS
)
from dv.models import (
    Allocation, BilateralInitiative, Indicator, News, NUTS, OrganisationRole,
    Programme, ProgrammeAllocation, Project, ProjectAllocation, State,
)
from dv.serializers import ProjectSerializer

CharField.register_lookup(Length, 'length')

# Used to determine the `is_ta` flag.
TA_CODES = frozenset({
    # 2014-2021
    'OT',
    # 2009-2014
    'PS13a',
    'PS13b',
    'PS14a',
    'PS14b',
    'PS15',
    'PS16',
})


def test_sentry(request):
    raise Exception('Testing sentry...')


@require_GET
def bilateral_initiatives(request):
    period = request.GET.get('period', DEFAULT_PERIOD)  # used in FE
    period_id = FUNDING_PERIODS_DICT[period]  # used in queries

    return JsonResponse(
        list(
            BilateralInitiative.objects.filter(funding_period=period_id)
            .values('state_id')
            .annotate(allocation=Sum('grant'), beneficiary=F('state_id'))
        )
    )


@require_GET
def overview(request):
    period = request.GET.get('period', DEFAULT_PERIOD)  # used in FE
    period_id = FUNDING_PERIODS_DICT[period]  # used in queries

    allocations = Allocation.objects.filter(
        funding_period=period_id,
    ).values(
        'financial_mechanism',
        'state',
    ).annotate(
        allocation=Sum('gross_allocation'),
    ).order_by('state', 'financial_mechanism')

    if period_id == 2:
        programme_allocations = ProgrammeAllocation.objects.filter(
            funding_period=period_id,
            outcome='Fund for bilateral relations',
        ).exclude(
             priority_sector_id__in=('PS13a', 'PS14a'),
        ).values(
            'financial_mechanism',
            'state',
        ).annotate(
            allocation=Sum('allocation'),
        )
        bilateral_fund = {
            (bf['financial_mechanism'], bf['state']): bf['allocation']
            for bf in programme_allocations
        }
    elif period_id == 3:
        bilateral_fund = {
            (bf['financial_mechanism'], bf['state']): bf['allocation']
            for bf in allocations.filter(programme_area__code__in=('TA02', 'TA04', 'OTBF'))
        }

    programme_query = Programme.objects.filter(
        funding_period=period_id,
        is_tap=False,
        is_bfp=False,
    ).prefetch_related(
        'states',
    ).order_by('code')

    programmes = defaultdict(list)
    for programme in programme_query:
        keys = product(
            programme.financial_mechanisms,
            programme.states.values_list('code', flat=True),
        )
        for key in keys:
            programmes[key].append(programme.code)

    dpp_programme_query = programme_query.filter(
        organisation_roles__role_code='DPP',
    ).distinct()
    dpp_programmes = defaultdict(list)
    for programme in dpp_programme_query:
        keys = product(
            programme.financial_mechanisms,
            programme.states.values_list('code', flat=True),
        )
        for key in keys:
            dpp_programmes[key].append(programme.code)

    project_query = Project.objects.filter(
        funding_period=period_id,
    ).exclude(
        # TODO check if values for 2009-2014 are the same, update tuple below otherwise
        status__in=('Planned',),
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
            key = (FM_EEA, project['state'])
            projects[key].append(project['code'])
            if project['is_dpp']:
                dpp_projects[key].append(project['code'])
            if project['is_continued_coop']:
                continued_coop[key].append(project['code'])
            if project['is_positive_fx']:
                positive_fx[key].append(project['code'])
        if project['is_norway']:
            key = (FM_NORWAY, project['state'])
            projects[key].append(project['code'])
            if project['is_dpp']:
                dpp_projects[key].append(project['code'])
            if project['is_continued_coop']:
                continued_coop[key].append(project['code'])
            if project['is_positive_fx']:
                positive_fx[key].append(project['code'])

    bilateral_initiative_query = BilateralInitiative.objects.filter(
        funding_period=period_id,
    ).select_related(
        'programme',
    )
    bilateral_initiatives = defaultdict(list)
    # TODO is it ok to decide if BI is EEA/Norway based on programme?
    for bi in bilateral_initiative_query:
        if bi.programme.is_eea:
            bilateral_initiatives[(FM_EEA, bi.state_id)].append(bi.code)
        if bi.programme.is_norway:
            bilateral_initiatives[(FM_NORWAY, bi.state_id)].append(bi.code)

    relevant_indicators = OVERVIEW_INDICATORS[period_id]
    indicator_query = Indicator.objects.filter(
        Q(achievement_eea__gt=0) | Q(achievement_norway__gt=0),
        funding_period=period_id,
        indicator__in=relevant_indicators.keys(),
    )
    indicators = defaultdict(lambda: defaultdict(int))
    for indicator in indicator_query:
        key = indicators[relevant_indicators[indicator.indicator]]
        if indicator.is_eea:
            key[(FM_EEA, indicator.state_id)] += indicator.achievement_eea
        if indicator.is_norway:
            key[(FM_NORWAY, indicator.state_id)] += indicator.achievement_norway

    out = []
    for allocation in allocations:
        state = allocation['state']
        financial_mechanism = allocation['financial_mechanism']
        key = (financial_mechanism, state)
        element = {
            'period': period,
            'fm': FM_DICT[financial_mechanism],
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
        for indicator in relevant_indicators.values():
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

    bilateral_fund = {}
    if period_id == 2:
        programme_allocations = ProgrammeAllocation.objects.filter(
            funding_period=period_id,
            outcome='Fund for bilateral relations',
        ).exclude(
             priority_sector_id__in=('PS13a', 'PS14a'),
        ).values(
            'financial_mechanism',
            'state',
            'programme_area',
        ).annotate(
            allocation=Sum('allocation'),
        )
        bilateral_fund = {
            (bf['financial_mechanism'], bf['state'], bf['programme_area']): bf['allocation']
            for bf in programme_allocations
        }
    elif period_id == 3:
        bilateral_fund = {
            (bf.financial_mechanism, bf.state_id, bf.programme_area_id): bf.gross_allocation
            for bf in allocations.filter(programme_area__code__in=('TA02', 'TA04', 'OTBF'))
        }

    indicators = Indicator.objects.filter(
        funding_period=period_id,
        programme__is_tap=False,
    ).values(
        'indicator',
        'header',
        'state_id',
        'programme_area_id'
    ).annotate(
        achievement_eea=Sum('achievement_eea'),
        achievement_norway=Sum('achievement_norway'),
    ).order_by(F('order').asc(nulls_last=True))

    results = defaultdict(lambda: defaultdict(dict))
    for indicator in indicators:
        if indicator['achievement_eea']:
            key = (FM_EEA, indicator['state_id'], indicator['programme_area_id'])
            results[key][indicator['header']].update({
                indicator['indicator']: {
                    'achievement': indicator['achievement_eea'],
                }
            })
        if indicator['achievement_norway']:
            key = (FM_NORWAY, indicator['state_id'], indicator['programme_area_id'])
            results[key][indicator['header']].update({
                indicator['indicator']: {
                    'achievement': indicator['achievement_norway'],
                }
            })

    programmes = defaultdict(dict)
    programme_query = Programme.objects.filter(
        funding_period=period_id,
        is_tap=False,
        is_bfp=False,
    ).prefetch_related(
        'states',
        'programme_areas',
    ).order_by('code')

    for programme in programme_query:
        keys = product(
            programme.financial_mechanisms,
            programme.states.values_list('code', flat=True),
            programme.programme_areas.values_list('id', flat=True),
        )
        for key in keys:
            programmes[key][programme.code] = {
                'name': programme.name,
                'url': programme.url,
            }

    out = []
    for allocation in allocations:
        state = allocation.state_id
        financial_mechanism = allocation.financial_mechanism
        programme_area = allocation.programme_area_id
        out.append({
            'period': period,
            'fm': FM_DICT[financial_mechanism],
            'sector': allocation.programme_area.priority_sector.name,
            'area': allocation.programme_area.name,
            'beneficiary': state,
            'is_ta': allocation.programme_area.priority_sector.code in TA_CODES,
            'allocation': allocation.gross_allocation,
            'net_allocation': allocation.net_allocation,
            'bilateral_allocation': bilateral_fund.get((financial_mechanism, state, programme_area), 0),
            'results': results[(financial_mechanism, state, programme_area)],
            'programmes': programmes[(financial_mechanism, state, programme_area)],
            'thematic': allocation.thematic,
        })

    return JsonResponse(out)


@require_GET
def sdg(request):
    period = request.GET.get('period', DEFAULT_PERIOD)  # used in FE
    period_id = FUNDING_PERIODS_DICT[period]  # used in queries

    allocation_query = ProgrammeAllocation.objects.filter(
        funding_period=period_id,
        programme_area__isnull=False,
    ).exclude(
        allocation=0,
    ).select_related(
        'programme',
    ).order_by('state', 'financial_mechanism')

    dataset = defaultdict(lambda: {
        'allocation': 0,
        'sectors': set(),
        'areas': set(),
        'programmes': {},
    })
    for allocation in allocation_query:
        key = (allocation.financial_mechanism, allocation.state_id, allocation.sdg_no)
        dataset[key]['allocation'] += allocation.allocation
        dataset[key]['sectors'].add(allocation.priority_sector_id)
        dataset[key]['areas'].add(allocation.programme_area_id)
        if not allocation.programme:
            continue
        dataset[key]['programmes'][allocation.programme.code] = {
            'name': allocation.programme.name,
            'url': allocation.programme.url,
        }

    indicators = Indicator.objects.filter(
        funding_period=period_id,
        programme__is_tap=False,
    ).values(
        'indicator',
        'header',
        'state_id',
        'sdg_no'
    ).annotate(
        achievement_eea=Sum('achievement_eea'),
        achievement_norway=Sum('achievement_norway'),
    ).order_by(F('order').asc(nulls_last=True))

    results = defaultdict(lambda: defaultdict(dict))
    for indicator in indicators:
        if indicator['achievement_eea']:
            key = (FM_EEA, indicator['state_id'], indicator['sdg_no'])
            results[key][indicator['header']].update({
                indicator['indicator']: {
                    'achievement': indicator['achievement_eea'],
                }
            })
        if indicator['achievement_norway']:
            key = (FM_EEA, indicator['state_id'], indicator['sdg_no'])
            results[key][indicator['header']].update({
                indicator['indicator']: {
                    'achievement': indicator['achievement_eea'],
                }
            })

    out = []
    for key, value in dataset.items():
        financial_mechanism, state, sdg_no = key
        out.append({
            'period': period,
            'fm': FM_DICT[financial_mechanism],
            'sectors': list(value['sectors']),
            'areas': list(value['areas']),
            'beneficiary': state,
            'allocation': value['allocation'],
            'results': results[key],
            'programmes': value['programmes'],
            'sdg_no': sdg_no,
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

    project_allocation_query = ProjectAllocation.objects.filter(
        funding_period=period_id,
    ).select_related(
        'project',
        'project__programme',
    )

    programmes = defaultdict(lambda: defaultdict(set))
    projects = defaultdict(set)
    project_allocations = defaultdict(int)
    for pja in project_allocation_query:
        project = pja.project
        key = (pja.financial_mechanism, pja.state_id, pja.programme_area_id)
        projects[key].add(project.code)
        project_allocations[key] += pja.allocation

        programme = project.programme
        if not programmes[key][programme.code]:
            programmes[key][programme.code] = {
                'name': programme.name,
                'url': programme.url,
                'nuts': defaultdict(lambda: defaultdict(set)),
            }
        programme_nuts = programmes[key][programme.code]['nuts'][project.nuts_id]
        programme_nuts['total'].add(project.code)
        if project.has_ended:
            programme_nuts['ended'].add(project.code)
        if project.is_positive_fx:
            programme_nuts['positive'].add(project.code)

    news_query = News.objects.filter(
        Q(project__funding_period=period_id) | Q(programmes__funding_period=period_id),
    ).prefetch_related(
        'project',
        'project__programme_areas',
        'programmes',
        'programmes__states',
        'programmes__programme_areas'
    ).order_by('-created')
    news = defaultdict(list)
    for item in news_query:
        if item.project:
            keys = product(
                item.project.financial_mechanisms,
                (item.project.state_id,),
                item.project.programme_areas.values_list('id', flat=True),
            )
        else:
            keys = chain(*[
                product(
                    programme.financial_mechanisms,
                    programme.states.values_list('code', flat=True),
                    programme.programme_areas.values_list('id', flat=True),
                )
                for programme in item.programmes.all()
            ])
        for key in keys:
            news[key].append({
                'title': html.unescape(item.title or ''),
                'link': item.link,
                'created': item.created,
                'summary': item.summary,
                'image': item.image,
                'nuts': item.project and item.project.nuts_id,
            })

    out = []
    for allocation in allocations:
        state = allocation.state_id
        financial_mechanism = allocation.financial_mechanism
        programme_area = allocation.programme_area_id
        key = (financial_mechanism, state, programme_area)
        out.append({
            'period': period,
            'fm': FM_DICT[financial_mechanism],
            'sector': allocation.programme_area.priority_sector.name,
            'area': allocation.programme_area.name,
            'beneficiary': state,
            'is_ta': allocation.programme_area.priority_sector.code in TA_CODES,
            'allocation': allocation.gross_allocation,
            'net_allocation': allocation.net_allocation,
            'programmes': programmes[key],
            'projects': projects[key],
            'project_allocation': project_allocations[key],
            'news': news[key],
            'thematic': allocation.thematic,
        })
    return JsonResponse(out, encoder=SetEncoder)


@require_GET
def partners(request):
    period = request.GET.get('period', DEFAULT_PERIOD)  # used in FE
    period_id = FUNDING_PERIODS_DICT[period]  # used in queries

    # List of programmes having DPP or dpp
    # Everything else will be grouped by these
    partnership_programmes_query = ProgrammeAllocation.objects.filter(
        funding_period=period_id,
        programme__organisation_roles__role_code__in=('DPP', 'PJDPP'),
    ).select_related(
        'programme_area',
        'priority_sector',
        'programme',
    ).distinct()

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
                'fm': FM_DICT[p.financial_mechanism],
            }
        key = (
            p.programme.code,
            p.programme_area.code if p.programme_area else None,
            p.state_id,
        )
        allocations[key] += p.allocation

    partnership_programmes_ids = partnership_programmes.keys()

    # Get donor countries for each programme
    programme_donors_query = OrganisationRole.objects.filter(
        funding_period=period_id,
        role_code__in=('DPP', 'PJDPP'),
    ).exclude(
        programme_id__isnull=True,
    ).values(
        'programme_id',
        'organisation__country',
    ).distinct()

    for p in programme_donors_query:
        partnership_programmes[p['programme_id']]['donors'].add(
            DONOR_STATES.get(p['organisation__country'], 'Intl')
        )

    # Get programme partners (DPP and PO)
    programme_partners_query = OrganisationRole.objects.filter(
        funding_period=period_id,
        programme_id__in=partnership_programmes_ids,
        role_code__in=('DPP', 'PO'),
    ).annotate(
        org_id=F('organisation_id'),
        name=F('organisation__name'),
        country=F('organisation__country'),
        nuts_id=F('organisation__nuts'),
        role=F('role_code'),
    ).values(
        'country',
        'org_id',
        'name',
        'programme_id',
        'role',
        'nuts_id',
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
                'nuts': pp['nuts_id'],
            }
            donor_programmes.add(programme_code)
        elif programme_code in donor_programmes:
            partnership_programmes[programme_code]['PO'][pp['org_id']] = {
                'name': pp['name'],
                'nuts': pp['nuts_id'],
            }

    # Get project partners (dpp and project promoters)
    project_partners_query = OrganisationRole.objects.filter(
        funding_period=period_id,
        programme_id__in=partnership_programmes_ids,
        role_code__in=('PJDPP', 'PJPT'),
        project__isnull=False,
    ).select_related(
        'project',
        'organisation',
    ).prefetch_related(
        'project__programme_areas',
    ).order_by('role_code').distinct()
    # Order by - for filtering out project promoters when no PJDPP is present

    projects, project_promoters, donor_project_partners = (
        defaultdict(dict), defaultdict(dict), defaultdict(dict)
    )
    donor_projects = set()
    project_nuts = {}

    for org_role in project_partners_query:
        # Projects have only one BS and one PA, so keep them separated
        project_code = org_role.project_id

        if org_role.role_code == 'PJPT':
            # Project promoters are stored by project, only for projects with dpp
            if project_code in donor_projects:
                project_promoters[project_code][org_role.organisation_id] = {
                    'name': org_role.organisation.name,
                    'nuts': org_role.organisation.nuts_id,
                }
                project_nuts[project_code]['dst'].append(org_role.organisation.nuts_id)
        elif org_role.role_code == 'PJDPP':
            donor_projects.add(project_code)

            # Donor project partner
            donor = DONOR_STATES.get(org_role.organisation.country, 'Intl')
            for programme_area in org_role.project.programme_areas.all():
                key = (
                    org_role.programme_id,
                    programme_area.code,
                    org_role.project.state_id,
                    donor
                )
                if org_role.organisation_id not in donor_project_partners[key]:
                    donor_project_partners[key][org_role.organisation_id] = {
                        'name': org_role.organisation.name,
                        'nuts': org_role.organisation.nuts_id,
                        # 'projects': [],
                        # project_count should be enough, trying to save 90KB
                        'prj': 0,
                    }
                # donor_project_partners[key][pp['organisation_id']]['projects'].append(pp['project_id'])
                donor_project_partners[key][org_role.organisation_id]['prj'] += 1
                # projects with dpp are stored for bilateral indicators
                if project_code not in projects[key]:
                    projects[key][project_code] = {
                        'is_dpp': org_role.project.is_dpp,
                        'has_ended': org_role.project.has_ended,
                        'continued_coop': org_role.project.is_continued_coop,
                        'improved_knowledge': org_role.project.is_improved_knowledge,
                        'src_nuts': [],
                        'dst_nuts': [],
                    }
                if project_code not in project_nuts:
                    project_nuts[project_code] = {
                        'src': [],
                        'dst': [],
                    }
                project_nuts[project_code]['src'].append(org_role.organisation.nuts_id)

    # Bilateral news, they are always related to programmes, not projects
    news_query = Programme.objects.filter(
        funding_period=period_id,
        news__is_partnership=True,
        code__in=partnership_programmes_ids,
        news__isnull=False,
    ).values(
        'code',
        'news__link',
        'news__summary',
        'news__image',
        'news__title',
        'news__created',
        'news__is_partnership',
    ).distinct()
    for item in news_query:
        partnership_programmes[item['code']]['news'].append({
            'title': html.unescape(item['news__title'] or ''),
            'link': item['news__link'],
            'created': item['news__created'],
            'summary': item['news__summary'],
            'image': item['news__image'],
        })

    def nuts_in_state(nuts, state_id):
        if not nuts:
            return
        if state_id == 'Intl':
            return not re.match('IS|LI|NO', nuts)
        return nuts.startswith(state_id)

    out = []
    for prg, item in partnership_programmes.items():
        # item: {'beneficiaries', 'news', 'areas', 'PO', 'donors', 'allocation'}
        for pa_code, pa_data in item['areas'].items():
            # pa_data = {'fm', 'sector', 'area'}
            for donor in item['donors']:
                for beneficiary in item['beneficiaries']:
                    key = (prg, pa_code, beneficiary)
                    key_donor = (prg, pa_code, beneficiary, donor)
                    # TODO Because of HU12 must get the amounts from Programme where possible
                    allocation = item['allocation']
                    if (len(item['beneficiaries']) > 1 or len(item['areas']) > 1):
                        allocation = allocations[key]
                    prj_promoters = {}
                    nuts_connections = {}
                    for prj_code in projects[key_donor]:
                        for key, value in project_promoters[prj_code].items():
                            prj_promoters[key] = value
                        for src in project_nuts[prj_code]['src']:
                            if not nuts_in_state(src, donor):
                                continue
                            for dst in project_nuts[prj_code]['dst']:
                                nuts_connections[(src, dst)] = {
                                    'src': src,
                                    'dst': dst,
                                }
                                if src not in projects[key_donor][prj_code]['src_nuts']:
                                    projects[key_donor][prj_code]['src_nuts'].append(src)
                                if dst not in projects[key_donor][prj_code]['dst_nuts']:
                                    projects[key_donor][prj_code]['dst_nuts'].append(dst)
                    row = {
                        'fm': pa_data['fm'],
                        'sector': pa_data['sector'],
                        'area': pa_data['area'],
                        'beneficiary': beneficiary,
                        'donor': donor,
                        'allocation': float(allocation),
                        'programme': prg,
                        'programmes': {
                            prg: {
                                'name': item['name'],
                                'url': item['url'],
                            }
                        },
                        'projects': projects[key_donor],
                        'prj_nuts': list(nuts_connections.values()),
                        'PO': item['PO'],
                        'PJDPP': donor_project_partners[key_donor],
                        'PJPT': prj_promoters,
                        'news': item['news'],
                    }
                    if donor_programme_partners[(prg, donor)]:
                        # This project has DPP, duplicate it for each partner from the current donor
                        for DPP_code, DPP_data in donor_programme_partners[(prg, donor)].items():
                            copy = dict(row)
                            # Assumption: name of DPP are unique
                            copy['DPP'] = DPP_data['name']
                            copy['DPP_nuts'] = DPP_data['nuts']
                            out.append(copy)
                    else:
                        # Still need to add rows without DPP if they have project partners
                        if row['PJDPP']:
                            if 'PO' in row:
                                del row['PO']  # Apparently we only need PO's for DPP programmes
                            out.append(row)
    return JsonResponse(out)


def beneficiary_detail(request, beneficiary):
    return project_nuts(request, beneficiary, force_nuts3=True)


def projects_beneficiary_detail(request, beneficiary):
    return project_nuts(request, beneficiary, force_nuts3=False)


def sdg_beneficiary_detail(request, beneficiary):
    # TODO This is very similar to project_nuts; refactor to reduce code duplication
    period = request.GET.get('period', DEFAULT_PERIOD)  # used in FE
    period_id = FUNDING_PERIODS_DICT[period]  # used in queries
    state_id = beneficiary

    try:
        state = State.objects.get(pk=state_id)
    except State.DoesNotExist:
        return JsonResponse({
            'error': f"Beneficiary state '{state_id}' does not exist."
        }, status=404)

    project_allocation_query = ProjectAllocation.objects.filter(
        funding_period=period_id,
        state=state,
    ).select_related(
        'project',
    )

    nuts3s = tuple(
        NUTS.objects
        .filter(nuts_versions__year=NUTS_VERSION_BY_PERIOD[period])
        .filter(code__startswith=state_id, code__length=5)
        .exclude(code__endswith='Z')  # skip extra-regio
        .order_by('code')
        .values_list('code', flat=True)
    )

    dataset = defaultdict(lambda: {
        'allocation': 0,
        'programmes': {},
        'areas': set(),
        'sectors': set(),
    })

    for pa in project_allocation_query:
        code = pa.project.nuts_id
        if len(code) > 2 and code.endswith('Z'):  # extra-regio
            code = code[:2]

        key = (
            pa.project.nuts_id,
            pa.financial_mechanism,
            pa.project.sdg_no,
        )
        if len(code) == 5:
            row = dataset[key]
            row['id'] = pa.project.nuts_id
            row['areas'].add(pa.programme_area_id)
            row['sectors'].add(pa.priority_sector_id)
            row['fm'] = FM_DICT[pa.financial_mechanism]
            row['allocation'] += pa.allocation
            row['programmes'][pa.project.programme_id] = pa.project.programme_id
            row['sdg_no'] = pa.project.sdg_no
            continue

        # else split allocation among children, and add project count to all children
        children = (nuts3s if len(code) == 2
                    else [n for n in nuts3s if n.startswith(code)])

        if len(children) == 0:
            # TODO: this is an error. log it, etc.
            continue

        allocation = pa.allocation / len(children)

        for nuts in children:
            childkey = (
                nuts,
                pa.financial_mechanism,
                pa.project.sdg_no,
            )
            row = dataset[childkey]
            row['id'] = nuts
            row['areas'].add(pa.programme_area_id)
            row['sectors'].add(pa.priority_sector_id)
            row['fm'] = FM_DICT[pa.financial_mechanism]
            row['allocation'] += allocation
            row['programmes'][pa.project.programme_id] = pa.project.programme_id
            row['sdg_no'] = pa.project.sdg_no

    out = []

    for key, row in dataset.items():
        # strip away some of that crazy precision
        row['allocation'] = row['allocation'].quantize(Decimal('1.00'))
        row['areas'] = list(row['areas'])
        row['sectors'] = list(row['sectors'])
        out.append(row)

    return JsonResponse(out)


def project_nuts(request, state_id, force_nuts3):
    """
    Returns NUTS3-level allocations for the given state.
    """

    period = request.GET.get('period', DEFAULT_PERIOD)  # used in FE
    period_id = FUNDING_PERIODS_DICT[period]  # used in queries

    try:
        state = State.objects.get(pk=state_id)
    except State.DoesNotExist:
        return JsonResponse({
            'error': f"Beneficiary state '{state_id}' does not exist."
        }, status=404)

    project_allocation_query = ProjectAllocation.objects.filter(
        funding_period=period_id,
        state=state,
    ).select_related(
        'project',
        'programme_area',
        'priority_sector',
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
        .filter(nuts_versions__year=NUTS_VERSION_BY_PERIOD[period])
        .filter(code__startswith=state_id, code__length=5)
        .exclude(code__endswith='Z')  # skip extra-regio
        .order_by('code')
        .values_list('code', flat=True)
    )

    dataset = defaultdict(lambda: {
        'allocation': 0,
        'projects': set(),
        'project_count': 0,
        'programmes': {},
    })

    for pa in project_allocation_query:
        code = pa.project.nuts_id
        if len(code) > 2 and code.endswith('Z'):  # extra-regio
            code = code[:2]

        key = (
            pa.project.nuts_id,
            pa.programme_area_id,
            pa.priority_sector_id,
            pa.financial_mechanism
        )
        if not force_nuts3 or len(code) == 5:
            row = dataset[key]
            row['id'] = pa.project.nuts_id
            row['area'] = pa.programme_area.name
            row['sector'] = pa.priority_sector.name
            row['fm'] = FM_DICT[pa.financial_mechanism]
            row['allocation'] += pa.allocation
            row['projects'].add(pa.project_id)
            row['programmes'][pa.project.programme_id] = pa.project.programme_id
            continue

        # else split allocation among children, and add project count to all children
        children = (nuts3s if len(code) == 2
                    else [n for n in nuts3s if n.startswith(code)])

        if len(children) == 0:
            # TODO: this is an error. log it, etc.
            continue

        allocation = pa.allocation / len(children)

        for nuts in children:
            childkey = (
                nuts,
                pa.programme_area_id,
                pa.priority_sector_id,
                pa.financial_mechanism
            )
            row = dataset[childkey]
            row['id'] = nuts
            row['area'] = pa.programme_area.name
            row['sector'] = pa.priority_sector.name
            row['fm'] = FM_DICT[pa.financial_mechanism]
            row['allocation'] += allocation
            row['projects'].add(pa.project_id)
            row['programmes'][pa.project.programme_id] = pa.project.programme_id

    out = []

    for key, row in dataset.items():
        # strip away some of that crazy precision
        row['allocation'] = row['allocation'].quantize(Decimal('1.00'))
        row['project_count'] = len(row['projects'])
        del row['projects']
        out.append(row)

    return JsonResponse(out)


class ProjectList(ListAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        queryset = ProjectAllocation.objects.all()

        period = self.request.GET.get('period', DEFAULT_PERIOD)  # used in FE
        period_id = FUNDING_PERIODS_DICT[period]  # used in queries
        queryset = queryset.filter(funding_period=period_id)

        programme = self.request.query_params.get('programme', None)
        if programme is not None:
            queryset = queryset.filter(project__programme_id=programme)

        beneficiary = self.request.query_params.get('beneficiary', None)
        if beneficiary is not None:
            queryset = queryset.filter(state_id=beneficiary)

        fm = FM_REVERSED_DICT.get(self.request.query_params.get('fm', None))
        if fm:
            queryset = queryset.filter(financial_mechanism=fm)

        programme_area_name = self.request.query_params.get('area', None)
        if programme_area_name:
            queryset = queryset.filter(programme_area__name=programme_area_name)
        else:
            # Don't add sector name if programme area is present
            sector_name = self.request.query_params.get('sector', None)
            if sector_name:
                queryset = queryset.filter(priority_sector__name=sector_name)

        nuts = self.request.query_params.get('nuts', None)
        if nuts:
            queryset = queryset.filter(project__nuts__code__startswith=nuts)

        is_dpp = self.request.query_params.get('is_dpp', None)
        if is_dpp:
            queryset = queryset.filter(project__is_dpp=True)

        donor = self.request.query_params.get('donor', None)
        if is_dpp and donor:
            donor_name = DONOR_STATES_REVERSED.get(donor)

            q = Q(project__organisation_roles__role_code='PJDPP')
            if donor_name:
                q &= Q(project__organisation_roles__organisation__country=donor_name)
            else:
                q &= ~Q(project__organisation_roles__organisation__country__in=EEA_DONOR_STATES.keys())
                # Django ORM generates an unnecessary complicated query here
            queryset = queryset.filter(q)

        return queryset.select_related(
            'project',
        ).annotate(
            total_allocation=Sum('allocation')
        ).order_by('project_id').distinct()
