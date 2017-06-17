from collections import OrderedDict, defaultdict, namedtuple
from decimal import Decimal
from rest_framework.generics import ListAPIView
from django.http import HttpResponseNotAllowed
from django.db.models import CharField
from django.db.models.expressions import F, Value
from django.db.models.aggregates import Count, Sum
from django.db.models.functions import Length, Concat
from django.db.models.query import Prefetch
from django.utils.text import slugify
from dv.lib.http import CsvResponse, JsonResponse
from dv.models import (
    Allocation,
    State, ProgrammeArea, Programme, Project,
    ProgrammeIndicator, ProgrammeOutcome,
    NUTS,
)
from dv.serializers import (
    ProjectSerializer,
)


CharField.register_lookup(Length, 'length')


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
    )
    programmes = set(ProgrammeOutcome.objects.all().select_related(
        'programme',
        'outcome__programme_area'
    ).values_list(
        'programme__code',
        'programme__name',
        'outcome__programme_area__code',
        'state__code'
    ).exclude(programme__isnull=True)
    )

    results = ProgrammeIndicator.objects.all().select_related(
        'indicator'
    ).exclude(achievement=0)

    out = []
    for a in allocations:
        out.append({
            # TODO: switch these to ids(?)
            'fm': a.financial_mechanism.grant_name,
            'sector': a.programme_area.priority_sector.name,
            'area': a.programme_area.name,
            'beneficiary': a.state.code,
            'allocation': a.gross_allocation,

            'bilateral_allocation': sum(p.allocation
                for o in a.programme_area.outcomes.all() if o.name == 'Fund for bilateral relations'
                    for p in o.programmes.all() if p.state_id == a.state_id),

            'results': {
                pi.result_text: {
                    pi.indicator.name: pi.achievement
                }
                for pi in results
                if pi.state_id == a.state.code and pi.programme_area_id == a.programme_area.code
            },
            'programmes': {
                p[0]: p[1] for p in programmes
                if p[2] == a.programme_area.code and p[3] == a.state.code
            },
        })

    """
    # use for testing with django-debug-toolbar:
    from django.http import HttpResponse
    from pprint import pformat
    return HttpResponse('<html><body><pre>%s</pre></body></html>' % pformat(out))
    """

    return JsonResponse(out)


def beneficiary_allocation_detail(request, beneficiary):
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
    allocations = (
        Project.objects.filter(state=state)
        .exclude(allocation=0)
        .annotate(**fields)
        .values(*fields.keys())
        .annotate(amount=Sum('allocation'))
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

    allocs = defaultdict(int)
    fkeys = tuple(fields.keys())
    codeidx = fkeys.index('id')
    #_verify1 = Decimal('0');

    for a in allocations:
        amount = a.pop('amount')
        #_verify1 += amount

        code = a['id']
        if len(code) > 2 and code.endswith('Z'): # extra-regio
            code = code[:2]

        # use fields' keys to ensure predictable order
        key = tuple(a[k] for k in fkeys)
        if len(code) == 5:
            allocs[key] += amount
            continue

        # else split among children
        children = (nuts3s if len(code) == 2
                    else [n for n in nuts3s if n.startswith(code)])

        if len(children) == 0:
            # TODO: this is an error. log it, etc.
            continue

        amount = amount / len(children)

        for nuts in children:
            childkey = key[:codeidx] + (nuts, ) + key[codeidx+1:]
            allocs[childkey] += amount

    allocations = []
    #_verify2 = Decimal('0');

    for key, amount in allocs.items():
        allocation = dict(zip(fkeys, key))
        #_verify2 += amount

        # strip away some of that crazy precision
        allocation['amount'] = amount.quantize(Decimal('1.00'))
        allocations.append(allocation)

    #print(_verify1, _verify2)
    return JsonResponse(allocations)


class ProjectList(ListAPIView):
    queryset = Project.objects.all().order_by('code')
    serializer_class = ProjectSerializer
