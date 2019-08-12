import re

from collections import defaultdict
from decimal import Decimal
from rest_framework.generics import ListAPIView
from django.http import HttpResponseNotAllowed
from django.db.models import CharField, Q
from django.db.models.expressions import F
from django.db.models.aggregates import Count, Sum
from django.db.models.functions import Length

from dv.lib.http import JsonResponse
from dv.models import (
    Allocation,
    State, Project,
    ProgrammeIndicator, ProgrammeOutcome,
    NUTS, News,
    Organisation_OrganisationRole,
)
from dv.serializers import (
    ProjectSerializer,
)
from dv.lib.utils import (
    EEA_DONOR_STATES,
    DONOR_STATES,
    DONOR_STATES_REVERSED,
)

CharField.register_lookup(Length, 'length')


def overview(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed()

    allocations = Allocation.objects.values(
        'financial_mechanism_id',
        'financial_mechanism__grant_name',
        'state_id'
    ).annotate(
        allocation=Sum('gross_allocation')
    ).order_by('state_id', 'financial_mechanism_id')

    programmes = ProgrammeOutcome.objects.all().select_related(
        'programme',
        'outcome__programme_area',
        'outcome__programme_area__priority_sector',
    ).values(
        'programme__code',
        'outcome__programme_area__financial_mechanism_id',
        'state__code',
        'programme__is_tap',
    ).exclude(
        programme__isnull=True,
    ).distinct()

    project_counts_raw = list(Project.objects.values(
        'financial_mechanism_id',
        'state_id',
    ).annotate(
        project_count=Count('code')
    ))

    project_counts = defaultdict(dict)
    for item in project_counts_raw:
        project_counts[item['financial_mechanism_id']].update({
            item['state_id']: item['project_count']
        })

    out = []
    for a in allocations:
        out.append({
            'fm': a['financial_mechanism__grant_name'],
            'beneficiary': a['state_id'],
            'allocation': float(a['allocation']),
            'programmes': [
                p['programme__code']
                for p in programmes
                if (
                    p['outcome__programme_area__financial_mechanism_id'] == a['financial_mechanism_id'] and
                    p['state__code'] == a['state_id'] and
                    not p['programme__is_tap']
                )
                # Exclude technical assistance programmes from this list
            ],
            'project_count': project_counts[a['financial_mechanism_id']].get(a['state_id'], 0)
        })

    return JsonResponse(out)


def grants(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed()

    allocations = Allocation.objects.all().select_related(
        'financial_mechanism',
        'state',
        'programme_area',
        'programme_area__priority_sector',
    ).prefetch_related(
        'programme_area__outcomes__programmes',
    ).exclude(
        gross_allocation=0
    )
    programmes = ProgrammeOutcome.objects.all().select_related(
        'programme',
        'outcome__programme_area',
    ).values(
        'programme__code',
        'programme__name',
        'outcome__programme_area__code',
        'state__code',
        'programme__url',
        'programme__is_tap'
    ).exclude(
        # Because sector Other has programme outcomes, but not programmes
        programme__isnull=True,
    ).distinct()

    all_results = ProgrammeIndicator.objects.all().select_related(
        'indicator'
    ).exclude(achievement=0)

    out = []
    for a in allocations:
        results = defaultdict(dict)
        for pi in all_results:
            if pi.state_id == a.state.code and pi.programme_area_id == a.programme_area.code:
                results[pi.result_text].update({
                    pi.indicator.name: {
                      'achievement': pi.achievement,
                      'order': pi.order,
                    }
                })
        out.append({
            # TODO: switch these to ids(?)
            'fm': a.financial_mechanism.grant_name,
            'sector': a.programme_area.priority_sector.name,
            'area': a.programme_area.name,
            'beneficiary': a.state.code,
            'is_ta': not a.programme_area.is_not_ta,
            'allocation': a.gross_allocation,
            'net_allocation': a.net_allocation,

            'bilateral_allocation': sum(p.allocation
                for o in a.programme_area.outcomes.all() if o.name == 'Fund for bilateral relations'
                    for p in o.programmes.all() if p.state_id == a.state_id),

            'results': results,
            'programmes': {
                p['programme__code']: {
                    'name': p['programme__name'],
                    'url': p['programme__url'],
                }
                for p in programmes
                if (
                    p['outcome__programme_area__code'] == a.programme_area.code and
                    p['state__code'] == a.state.code and
                    not p['programme__is_tap']
                    # Exclude technical assistance programmes from this list
                )
            },
        })

    """
    # use for testing with django-debug-toolbar:
    from django.http import HttpResponse
    from pprint import pformat
    return HttpResponse('<html><body><pre>%s</pre></body></html>' % pformat(out))
    """

    return JsonResponse(out)


def projects(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed()

    allocations = Allocation.objects.all().select_related(
        'financial_mechanism',
        'state',
        'programme_area',
        'programme_area__priority_sector',
    ).prefetch_related(
        'programme_area__outcomes__programmes',
    ).exclude(
        gross_allocation=0
    )

    # get the real state_id from ProgrammeOutcome, refs IN22
    programmes = ProgrammeOutcome.objects.all().select_related(
        'programme',
        'outcome__programme_area',
    ).values(
        'programme__code',
        'programme__name',
        'outcome__programme_area__code',
        'state__code',
        'programme__url',
        'programme__is_tap'
    ).exclude(
        # Because sector Other has programme outcomes, but not programmes
        programme__isnull=True,
    ).distinct()

    project_nuts_raw = Project.objects.values(
        'financial_mechanism_id',
        'programme_area_id',
        'state_id',
        'code',
        'nuts',
        'programme_id',
        'has_ended',
        'is_positive_fx',
    ).annotate(
        project_count=Count('code'),
        total_allocation=Sum('allocation')
    )
    project_nuts = defaultdict(lambda: defaultdict(dict))
    project_allocation = defaultdict(float)
    project_count = defaultdict(int)
    for item in project_nuts_raw:
        key = item['financial_mechanism_id'] + item['programme_area_id'] + item['state_id']
        project_count[key] += item['project_count']
        project_allocation[key] += float(item['total_allocation'])
        key = key + item['programme_id']
        nuts = project_nuts[key][item['nuts']]
        if not nuts:
            nuts = project_nuts[key][item['nuts']] = {
                'count': 0,
                'ended': 0,
                'positive': 0,
            }
        nuts['count'] += item['project_count']
        if item['has_ended']:
            nuts['ended'] += item['project_count']
            if item['is_positive_fx']:
                # Only count positive effects for projects which have ended
                nuts['positive'] += item['project_count']

    news_raw = (
        News.objects.all()
        .select_related(
            'project',
        ).exclude(project_id__isnull=True)
        .order_by('-created')
    )
    news = defaultdict(list)
    for item in news_raw:
        key = (
            item.project.financial_mechanism_id +
            item.project.programme_area_id +
            item.project.state_id
        )
        news[key].append({
            'title': item.title,
            'link': item.link,
            'created': item.created,
            'summary': item.summary,
            'image': item.image,
            'nuts': item.project.nuts,
        })

    out = []
    for a in allocations:
        key = a.financial_mechanism.code + a.programme_area.code + a.state_id
        out.append({
            # TODO: switch these to ids(?)
            'fm': a.financial_mechanism.grant_name,
            'sector': a.programme_area.priority_sector.name,
            'area': a.programme_area.name,
            'beneficiary': a.state.code,
            'is_ta': not a.programme_area.is_not_ta,
            'allocation': a.gross_allocation,
            'net_allocation': a.net_allocation,
            'project_allocation': project_allocation.get(key, 0),
            'project_count': project_count.get(key, 0),
            'news': news.get(key, []),
            'programmes': {
                p['programme__code']: {
                    'name': p['programme__name'],
                    'url': p['programme__url'],
                    'nuts': project_nuts[key + p['programme__code']],
                }
                for p in programmes
                if (
                    p['outcome__programme_area__code'] == a.programme_area.code and
                    p['state__code'] == a.state.code and
                    not p['programme__is_tap']
                    # Exclude technical assistance programmes from this list
                )
            },
        })

    """
    # use for testing with django-debug-toolbar:
    from django.http import HttpResponse
    from pprint import pformat
    return HttpResponse('<html><body><pre>%s</pre></body></html>' % pformat(out))
    """

    return JsonResponse(out)


def partners(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed()

    def nuts_in_state(nuts, state_id):
        if state_id == 'Intl':
            return not re.match('IS|LI|NO', nuts)
        else:
            return nuts.startswith(state_id)

    # List of programmes having DPP or dpp
    # Everything else will be grouped by these
    partnership_programmes_raw = ProgrammeOutcome.objects.all().select_related(
        'programme',
        'outcome__programme_area',
        'outcome__programme_area__priority_sector',
        'outcome__programme_area__financial_mechanism',
        'programme__organisation_roles',
    ).annotate(
        prg_code=F('programme__code'),
        name=F('programme__name'),
        url=F('programme__url'),
        pa_code=F('outcome__programme_area__code'),
        pa_name=F('outcome__programme_area__name'),
        sector=F('outcome__programme_area__priority_sector__name'),
        fm=F('outcome__programme_area__financial_mechanism__grant_name'),
        allocation_eea=F('programme__allocation_eea'),
        allocation_norway=F('programme__allocation_norway'),
    ).values(
        'prg_code',
        'name',
        'url',
        'pa_code',
        'pa_name',
        'sector',
        'fm',
        'state__code',  # get the real beneficiary state from ProgrammeOutcome, because IN22
        'allocation_eea',
        'allocation_norway',
    ).exclude(
        # Because sector Other has programme outcomes, but not programmes
        programme__isnull=True,
    ).filter(
        programme__organisation_roles__organisation_role_id__in=['DPP', 'PJDPP']
    ).distinct()

    partnership_programmes = {}
    for p in partnership_programmes_raw:
        if p['prg_code'] not in partnership_programmes:
            partnership_programmes[p['prg_code']] = {
                'name': p['name'],
                'url': p['url'],
                'areas': {},
                'beneficiaries': set(),
                'donors': set(),
                'DPP': {},
                'PO': {},
                'news': [],
                'allocation': p['allocation_eea'] + p['allocation_norway'],
            }
        partnership_programmes[p['prg_code']]['beneficiaries'].add(p['state__code'])
        partnership_programmes[p['prg_code']]['areas'][p['pa_code']] = {
            'area': p['pa_name'],
            'sector': p['sector'],
            'fm': p['fm'],
        }

    partnership_programmes_ids = partnership_programmes.keys()

    # Compute allocations per Programme and Programme area
    allocations_raw = list(ProgrammeOutcome.objects.all().select_related(
        'outcome',
    ).filter(
        programme_id__in=partnership_programmes_ids
    ).values(
        'programme_id',
        'state_id',
        'outcome__programme_area_id',
    ).annotate(
        allocation=Sum('allocation')
    ))
    allocations = {}
    for item in allocations_raw:
        key = (
            item['programme_id'] +
            item['outcome__programme_area_id'] +
            item['state_id']
        )
        allocations[key] = item['allocation']

    # Get donor countries for each programme
    programme_donors_raw = Organisation_OrganisationRole.objects.all().select_related(
        'organisation'
    ).values(
        'programme_id',
        'organisation__country'
    ).exclude(
        programme_id__isnull=True,
    ).filter(
        organisation_role_id__in=['DPP', 'PJDPP']
    ).distinct()

    for p in programme_donors_raw:
        partnership_programmes[p['programme_id']]['donors'].add(
            DONOR_STATES.get(p['organisation__country'], 'Intl')
        )
    # Get programme partners (DPP and PO)
    PP_raw = Organisation_OrganisationRole.objects.all().select_related(
        'organisation',
        'programme',
    ).filter(
        programme_id__in=partnership_programmes_ids
    ).annotate(
        org_id=F('organisation_id'),
        name=F('organisation__name'),
        country=F('organisation__country'),
        role=F('organisation_role_id'),
        nuts=F('organisation__nuts'),
    ).values(
        'country',
        'org_id',
        'name',
        'programme_id',
        'role',
        'nuts',
    ).filter(
        organisation_role_id__in=['DPP', 'PO']
    ).order_by('organisation_role_id').distinct()
    # Order by - for filtering out PO when no DPP is present

    donor_programme_partners = defaultdict(dict)
    donor_programmes = set()
    # Donor programmes = only those having a DPP
    for pp in PP_raw:
        prg_code = pp['programme_id']
        if pp['role'] == 'DPP':
            donor = DONOR_STATES.get(pp['country'], 'Intl')
            key = prg_code + donor
            donor_programme_partners[key][pp['org_id']] = {
                'name': pp['name'],
                'nuts': pp['nuts'],
            }
            donor_programmes.add(prg_code)
        elif prg_code in donor_programmes:
            partnership_programmes[prg_code]['PO'][pp['org_id']] = {
                'name': pp['name'],
                'nuts': pp['nuts'],
            }

    # Get project partners (dpp and project promoters)
    pp_raw = Organisation_OrganisationRole.objects.all().select_related(
        'organisation',
        'project',
    ).filter(
        programme_id__in=partnership_programmes_ids
    ).values(
        'organisation__country',
        'organisation_id',
        'organisation__name',
        'organisation__nuts',
        'project_id',
        'programme_id',
        'project__state_id',
        'project__programme_area_id',
        'project__is_dpp',
        'project__has_ended',
        'project__is_continued_coop',
        'project__is_improved_knowledge',
        'organisation_role_id',
    ).filter(
        organisation_role_id__in=['PJDPP', 'PJPT']
    ).order_by('organisation_role_id').distinct()
    # Order by - for filtering out project promoters when no PJDPP is present

    projects, project_promoters, donor_project_partners = (
        defaultdict(dict), defaultdict(dict), defaultdict(dict)
    )
    donor_projects = set()
    project_nuts = {}

    # There are very special cases like BG04-0016, when project promoters vary by donor

    for pp in pp_raw:
        # Projects have only one BS and one PA, so keep them separated
        prj_code = pp['project_id']

        if pp['organisation_role_id'] == 'PJPT':
            # Project promoters are stored by project, only for projects with dpp
            if (prj_code in donor_projects):
                project_promoters[prj_code][pp['organisation_id']] = {
                    'name': pp['organisation__name'],
                    'nuts': pp['organisation__nuts'],
                }
                project_nuts[prj_code]['dst'].append(pp['organisation__nuts'])
        elif pp['organisation_role_id'] == 'PJDPP':
            donor_projects.add(prj_code)
            # Donor project partner
            donor = DONOR_STATES.get(pp['organisation__country'], 'Intl')
            key = (
                pp['programme_id'] +
                pp['project__programme_area_id'] +
                pp['project__state_id'] +
                donor
            )
            if pp['organisation_id'] not in donor_project_partners[key]:
                donor_project_partners[key][pp['organisation_id']] = {
                    'name': pp['organisation__name'],
                    'nuts': pp['organisation__nuts'],
                    # 'projects': [],
                    # project_count should be enough, trying to save 90KB
                    'prj': 0,
                }
            # donor_project_partners[key][pp['organisation_id']]['projects'].append(pp['project_id'])
            donor_project_partners[key][pp['organisation_id']]['prj'] += 1
            # projects with dpp are stored for bilateral indicators
            if prj_code not in projects[key]:
                projects[key][prj_code] = {
                    'is_dpp': pp['project__is_dpp'],
                    'has_ended': pp['project__has_ended'],
                    'continued_coop': pp['project__is_continued_coop'],
                    'improved_knowledge': pp['project__is_improved_knowledge'],
                    'src_nuts': [],
                    'dst_nuts': [],
                }
            if prj_code not in project_nuts:
                project_nuts[prj_code] = {
                    'src': [],
                    'dst': [],
                }
            project_nuts[prj_code]['src'].append(pp['organisation__nuts'])

    # Bilateral news, they are always related to programmes, not projects
    news_raw = ProgrammeOutcome.objects.all(
    ).filter(
        programme__news__is_partnership=True,
        programme_id__in=partnership_programmes_ids
    ).values(
        'programme_id',
        'programme__news__link',
        'programme__news__summary',
        'programme__news__image',
        'programme__news__title',
        'programme__news__created',
        'programme__news__is_partnership',
    ).distinct()
    for item in news_raw:
        partnership_programmes[item['programme_id']]['news'].append({
            'title': item['programme__news__title'],
            'link': item['programme__news__link'],
            'created': item['programme__news__created'],
            'summary': item['programme__news__summary'],
            'image': item['programme__news__image'],
        })

    out = []
    for prg, item in partnership_programmes.items():
        # item: {'beneficiaries', 'news', 'areas', 'PO', 'donors', 'allocation'}
        for pa_code, pa_data in item['areas'].items():
            # pa_data = {'fm', 'sector', 'area'}
            for donor in item['donors']:
                for beneficiary in item['beneficiaries']:
                    key = prg + pa_code + beneficiary
                    key_donor = prg + pa_code + beneficiary + donor
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
                                nuts_connections[src + dst] = {
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
                    if donor_programme_partners[prg + donor]:
                        # This project has DPP, duplicate it for each partner from the current donor
                        for DPP_code, DPP_data in donor_programme_partners[prg + donor].items():
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

    """
    # use for testing with django-debug-toolbar:
    from django.http import HttpResponse
    from pprint import pformat
    return HttpResponse('<html><body><pre>%s</pre></body></html>' % pformat(out))
    """

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
        'programme_id': F('programme_id'),
    }
    data = (
        Project.objects.filter(state=state)
        .annotate(**fields)
        .values(*fields.keys())
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
