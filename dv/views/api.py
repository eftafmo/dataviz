from collections import OrderedDict, defaultdict, namedtuple
from django.db.models import CharField
from django.db.models.expressions import F, Value
from django.db.models.aggregates import Sum
from django.db.models.functions import Length, Concat
from django.utils.text import slugify
from dv.lib.http import CsvResponse, JsonResponse
from dv.models import State, ProgrammeArea, Project


CharField.register_lookup(Length, 'length')


def beneficiaries_fm_gross_allocation(request):
    states = State.objects.all().only(
        'code', 'name',
        'gross_allocation_eea', 'gross_allocation_norway',
    )
    data = []
    fields = 'donor', 'beneficiary', 'amount'
    Allocation = namedtuple('Allocation', " ".join(fields))

    for state in states:
        if state.gross_allocation_norway:
            data.append(Allocation(
                "Norway", state.name, state.gross_allocation_norway
            ))
        if state.gross_allocation_eea:
            data.append(Allocation(
                "EEA", state.name, state.gross_allocation_eea
            ))

    return CsvResponse(data, fields)

def sectors_areas_allocation(request):
    """
    Returns a list of
    {
        name: "priority sector",
        children: [
            {
                name: "programme area",
                allocation: {
                    "financial mechanism": amount,
                    ...
                },
            },
            ...
        ]
    },
    ...
    """
    items = (
        ProgrammeArea.objects.select_related('priority_sector')
        .exclude(gross_allocation=0)
        .only(
            'priority_sector__type', 'priority_sector__name',
            'short_name', 'name', 'gross_allocation'
        )
        .order_by(
            'priority_sector__name', 'priority_sector__type', 'short_name'
        )
    )

    sectors = defaultdict(lambda: defaultdict(dict))

    for item in items:
        sector_name, area_name, fm, allocation = (
            item.priority_sector.name.capitalize(),
            item.name,
            str(item.priority_sector.type),
            round(item.gross_allocation),
        )

        sector = sectors[sector_name]
        area = sector[area_name]
        area[fm] = allocation

    out = tuple(
        OrderedDict((
            ("id", slugify(sector)),
            ("name", sector),
            ("children", tuple(
                OrderedDict((
                    ("id", slugify(area)),
                    ("name", area),
                    ("allocation", allocations)
                ))
                for area, allocations in areas.items()
            ))
        ))
        for sector, areas in sectors.items()
    )

    return JsonResponse(out)

def beneficiary_allocation(request):
    fields = OrderedDict((
        ('id', 'code'),
        ('name', 'name'),
        ('EEA', 'gross_allocation_eea'),
        ('Norway', 'gross_allocation_norway'),
    ))

    states = (
        State.objects.all().values_list(*fields.values())
    )

    return CsvResponse(states, fields.keys())

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
            pa=F('outcome__programme_area__name'),
            ps=F('outcome__programme_area__priority_sector__name'),
            # TODO: remove this Concat trick once we get rid of fm enums
            fm=Concat(
                F('outcome__programme_area__priority_sector__type'),
                Value(''),
                output_field=CharField()
            ),
        )
        .values('nuts', 'pa', 'ps', 'fm')
        .annotate(amount=Sum('allocation'))
    )

    return JsonResponse(list(allocations))
