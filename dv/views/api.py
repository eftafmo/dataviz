from collections import OrderedDict, defaultdict, namedtuple

from django.http import HttpResponseNotAllowed
from django.utils.text import slugify
from dv.lib.http import CsvResponse, JsonResponse
from dv.models import State, ProgrammeArea, Allocation


def grants(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed()

    allocations = Allocation.objects.all().select_related(
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
            'FMCode': a.financial_mechanism_id,
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
