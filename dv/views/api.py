from collections import defaultdict
from decimal import Decimal
from rest_framework.generics import ListAPIView
from django.http import HttpResponseNotAllowed
from django.db.models import CharField
from django.db.models.expressions import F
from django.db.models.aggregates import Count, Sum
from django.db.models.functions import Length

from django.utils.text import slugify
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
        'outcome__programme_area__priority_sector__type_id',
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
                    p['outcome__programme_area__priority_sector__type_id'] == a['financial_mechanism_id'] and
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
            'is_not_ta': a.programme_area.is_not_ta,
            'allocation': a.gross_allocation,

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

    project_counts_raw = Project.objects.values(
        'financial_mechanism_id',
        'programme_area_id',
        'state_id',
        'has_ended',
        'is_positive_fx'
    ).annotate(
        project_count=Count('code')
    )

    project_count, project_count_ended, project_count_positive = (
        defaultdict(int), defaultdict(int), defaultdict(int)
    )
    for item in project_counts_raw:
        key = item['financial_mechanism_id'] + item['programme_area_id'] + item['state_id']
        project_count[key] += item['project_count']
        if item['has_ended']:
            project_count_ended[key] += item['project_count']
            if item['is_positive_fx']:
                # Only count positive effects for projects which have ended
                project_count_positive[key] += item['project_count']

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
            'is_not_ta': a.programme_area.is_not_ta,
            'allocation': a.gross_allocation,
            'project_count': project_count.get(key, 0),
            'project_count_ended': project_count_ended.get(key, 0),
            'project_count_positive': project_count_positive.get(key, 0),
            'news': news.get(key, []),
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


def partners(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed()

    # Because everything else is International
    DONOR_STATES = {
        'Norway': 'Norway',
        'Iceland': 'Iceland',
        'Liechtenstein': 'Liechtenstein',
    }

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

    # List of programmes having DPP or dpp, grouped by PA and BS
    # Needed for size of PS/PA chart slices
    partnership_programmes = ProgrammeOutcome.objects.all().select_related(
        'programme',
        'outcome__programme_area',
        'programme__organisation_roles',
    ).values(
        'programme__code',
        'programme__name',
        'outcome__programme_area__code',
        'state__code',  # get the real state_id from ProgrammeOutcome, because IN22
    ).exclude(
        # Because sector Other has programme outcomes, but not programmes
        programme__isnull=True,
        programme__is_tap=True,  # not really needed
    ).filter(
        programme__organisation_roles__organisation_role_id__in=['DPP', 'PJDPP']
    ).distinct()

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

    programme_donors = defaultdict(list)
    for item in programme_donors_raw:
        programme_donors[item['programme_id']].append(
            DONOR_STATES.get(
                item['organisation__country'], 'International'
            )
        )

    # Get Donor *Programme* Partners by PA and BS (via programmes)
    DPP_raw = ProgrammeOutcome.objects.all().select_related(
        'programme',
        'outcome__programme_area',
    ).prefetch_related(
        'programme__organisation_roles',
        'programme__organisation_roles__organisation',
    ).exclude(
        # Because sector Other has programme outcomes, but not programmes
        programme_id__isnull=True,
    ).filter(
        programme__organisation_roles__organisation_role_id='DPP'
    ).values(
        'outcome__programme_area__code',
        'state__code',  # get the real state_id from ProgrammeOutcome, because IN22
        'programme_id',
        'programme__organisation_roles__organisation_id',
        'programme__organisation_roles__organisation__country',
        'programme__organisation_roles__organisation__name',
    ).distinct()
    DPP = defaultdict(lambda: defaultdict(dict))
    for item in DPP_raw:
        key = item['outcome__programme_area__code'] + item['state__code']
        org_id = item['programme__organisation_roles__organisation_id']
        donor_state = DONOR_STATES.get(
            item['programme__organisation_roles__organisation__country'],
            'International'
        )
        if org_id not in DPP[key][donor_state]:
            DPP[key][donor_state][org_id] = {
                'name': item['programme__organisation_roles__organisation__name'],
                'programmes': [item['programme_id']],
            }
        else:
            DPP[key][donor_state][org_id]['programmes'].append(item['programme_id'])

    # Statistics for donor *project* partners
    project_counts_raw = Organisation_OrganisationRole.objects.all().select_related(
        'organisation',
        'project',
    ).values(
        'organisation__country',
        'project_id',
        'programme_id',
        'project__state_id',
        'project__programme_area_id',
    ).filter(
        organisation_role_id='PJDPP'
    ).distinct()

    dpp_project_count, dpp_programmes, dpp_states = (
        defaultdict(lambda: defaultdict(int)),
        defaultdict(lambda: defaultdict(dict)),
        defaultdict(lambda: defaultdict(dict)),
    )
    for item in project_counts_raw:
        key = item['project__programme_area_id'] + item['project__state_id']
        donor_state = DONOR_STATES.get(
            item['organisation__country'],
            'International'
        )
        dpp_project_count[key][donor_state] += 1
        dpp_programmes[key][donor_state][item['programme_id']] = item['programme_id']
        dpp_states[key][donor_state][item['project__state_id']] = item['project__state_id']

    # Bilateral news, they are always related to programmes, not projects
    news_raw = ProgrammeOutcome.objects.all(
    ).filter(
        # Because sector Other has programme outcomes, but not programmes
        programme__isnull=False,
        programme__news__is_partnership=True
    ).values(
        'outcome__programme_area__code',
        'state__code',  # get the real state_id from ProgrammeOutcome, because IN22
        'programme__news__link',
        'programme__news__summary',
        'programme__news__image',
        'programme__news__title',
        'programme__news__created',
        'programme__news__is_partnership',
    ).distinct()

    news = defaultdict(list)
    for item in news_raw:
        key = item['outcome__programme_area__code'] + item['state__code']
        news[key].append({
            'title': item['programme__news__title'],
            'link': item['programme__news__link'],
            'created': item['programme__news__created'],
            'summary': item['programme__news__summary'],
            'image': item['programme__news__image'],
        })

    out = []
    for a in allocations:
        key = a.programme_area.code + a.state_id
        out.append({
            # TODO: switch these to ids(?)
            'fm': a.financial_mechanism.grant_name,
            'sector': a.programme_area.priority_sector.name,
            'area': a.programme_area.name,
            'beneficiary': a.state.code,
            'allocation': a.gross_allocation,
            'dpp_project_count': dpp_project_count.get(key, 0),
            'dpp_programmes': dpp_programmes.get(key, {}),
            'dpp_states': dpp_states.get(key, {}),
            'news': news.get(key, []),
            'partnership_programmes': {
                p['programme__code']: {
                    'donor_states': programme_donors[p['programme__code']]
                }
                for p in partnership_programmes
                if (
                    p['outcome__programme_area__code'] == a.programme_area.code and
                    p['state__code'] == a.state.code
                )
            },
            'donor_programme_partners': DPP.get(key, {})
        })

    """
    # use for testing with django-debug-toolbar:
    from django.http import HttpResponse
    from pprint import pformat
    return HttpResponse('<html><body><pre>%s</pre></body></html>' % pformat(out))
    """

    return JsonResponse(out)


def beneficiary_detail(request, beneficiary):
    """
    Returns NUTS3-level allocations for the given state.
    """
    try:
        state = State.objects.get_by_natural_key(beneficiary)
    except State.DoesNotExist:
        return JsonResponse({
            'error': "Beneficiary state '%s' does not exist." % beneficiary
        }, status=404)

    # Note: if project's PA stops going through Outcome, update below
    fields = {
        'id': F('nuts'),
        'area': F('outcome__programme_area__name'),
        'sector': F('outcome__programme_area__priority_sector__name'),
        'fm': F('outcome__programme_area__priority_sector__type__grant_name'),
    }
    data = (
        Project.objects.filter(state=state)
        .exclude(allocation=0)
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
        .exclude(code__endswith="Z") # skip extra-regio
        .order_by('code')
        .values_list('code', flat=True)
    )

    dataset = defaultdict(lambda: {
        'allocation': 0,
        'project_count': 0,
    })
    fkeys = tuple(fields.keys())
    codeidx = fkeys.index('id')
    #_verify1 = Decimal('0');

    for a in data:
        allocation = a.pop('allocation')
        project_count = a.pop('project_count')
        #_verify1 += allocation

        code = a['id']
        if len(code) > 2 and code.endswith('Z'): # extra-regio
            code = code[:2]

        # use fields' keys to ensure predictable order
        key = tuple(a[k] for k in fkeys)
        if len(code) == 5:
            row = dataset[key]
            row['allocation'] += allocation
            row['project_count'] += project_count
            continue

        # else split allocation among children,
        # and add project count to all children
        # TODO: or ignore it entirely. customer input needed.
        children = (nuts3s if len(code) == 2
                    else [n for n in nuts3s if n.startswith(code)])

        if len(children) == 0:
            # TODO: this is an error. log it, etc.
            continue

        allocation = allocation / len(children)

        for nuts in children:
            childkey = key[:codeidx] + (nuts, ) + key[codeidx+1:]
            row = dataset[childkey]
            row['allocation'] += allocation
            row['project_count'] += project_count

    out = []
    #_verify2 = Decimal('0');

    for key, row in dataset.items():
        item = dict(zip(fkeys, key))
        #_verify2 += allocation

        # strip away some of that crazy precision
        row['allocation'] = row['allocation'].quantize(Decimal('1.00'))

        item.update(row)
        out.append(item)

    #print(_verify1, _verify2)
    return JsonResponse(out)

class ProjectList(ListAPIView):
    queryset = Project.objects.all().order_by('code')
    serializer_class = ProjectSerializer
