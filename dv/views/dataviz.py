from django.http import Http404
from django.shortcuts import render as _render
from django.urls import reverse


ALLOCATION_PERIODS = {
    "2014-2021": [
        'overview',
        'funding',
        'cooperation',
        'projects',
        'global_goals',
    ],
    "2009-2014": [
        'overview',
        'funding',
        'cooperation',
        'projects',
    ],
    "compare": [
        'beneficiary_states',
        'sectors',
    ]
    #"2004-2009": [
    #
    #],
}


def get_menu():
    return [
        {
            "id": period,
            "url": reverse('frontend:period', args=[period]),
            "scenarios": [
                {
                    "id": scenario,
                    "name": scenario.title().replace("_", " "),
                    "url": (
                        reverse('frontend:period', args=[period])
                        if scenario == 'overview' else
                        reverse('frontend:scenario', args=[period, scenario])
                    )
                }

                for scenario in scenarios
            ]
        }

        for period, scenarios in ALLOCATION_PERIODS.items()
    ]


def render(request, period, scenario=None):
    """
    Renders the data visualisation template
    for the given allocation period and scenario.
    """

    if scenario is None and period == "compare":
        scenario = 'beneficiary_states'
    elif scenario is None:
        scenario = 'overview'

    if scenario not in ALLOCATION_PERIODS[period]:
        raise Http404()

    context = {
        "PERIOD": period,
        "SCENARIO": scenario,
    }

    template = '%s.html' % scenario

    return _render(request, template, context)
