from collections import OrderedDict, defaultdict, namedtuple
from django.http import HttpResponseNotAllowed
from django.db.models import CharField
from django.db.models.expressions import F, Value
from django.db.models.aggregates import Sum
from django.db.models.functions import Length, Concat
from django.utils.text import slugify
from dv.lib.http import CsvResponse, JsonResponse
from dv.models import (
    Allocation,
    State, ProgrammeArea, Project,
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
        # TODO figure out how to use Prefetch() here to filter outcome.name from the begining
        'programme_area__outcomes__programmes',
    )
    out = []
    for a in allocations:
        out.append({
            'BSCode': a.state.code,
            'BSName': a.state.name,
            'FMCode': a.financial_mechanism.code,
            'FMName': a.financial_mechanism.grant_name,
            'PACode': a.programme_area.code,
            'PAShort': a.programme_area.short_name,
            'PAName': a.programme_area.name,
            'PSCode': a.programme_area.priority_sector.code,
            'PSName': a.programme_area.priority_sector.name,
            'GrossAlloc': a.gross_allocation,
            'NetAlloc': a.net_allocation,
            # Make sure you select the exact querySet from related manager as we did on prefetch_related
            # That is all(). This is why we filter the outcome.name in python.
            # Otherwise the prefetch is useless and this will take a *lot* of time
            'BilateralAlloc': sum(p.allocation
                for o in a.programme_area.outcomes.all() if o.name == 'Fund for bilateral relations'
                    for p in o.programmes.all() if p.state_id == a.state_id),
        })
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
    allocations = (
        Project.objects.filter(state=state)
        # TODO: load parent codes too and split amongst children (?)
        .filter(nuts__length=5)
        .exclude(allocation=0)
        .annotate(
            id=F('nuts'),
            pa=F('outcome__programme_area__name'),
            ps=F('outcome__programme_area__priority_sector__name'),
            # TODO: remove this Concat trick once we get rid of fm enums
            fm=Concat(
                F('outcome__programme_area__priority_sector__type'),
                Value(''),
                output_field=CharField()
            ),
        )
        .values('id', 'pa', 'ps', 'fm')
        .annotate(amount=Sum('allocation'))
    )

    return JsonResponse(list(allocations))
