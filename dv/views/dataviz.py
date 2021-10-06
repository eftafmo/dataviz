from django.http import Http404
from django.shortcuts import render as _render
from django.urls import reverse


ALLOCATION_PERIODS = {
    "2014-2021": [
        "overview",
        "funding",
        "cooperation",
        "projects",
        "global_goals",
    ],
    "2009-2014": [
        "overview",
        "funding",
        "cooperation",
        "projects",
    ],
    "compare": [
        "beneficiary_states",
        "sectors",
    ],
}


def get_menu(request):
    current_period = request.resolver_match.kwargs.get("period")
    current_scenario = request.resolver_match.kwargs.get("scenario")

    menu_items = []

    for period, scenarios in ALLOCATION_PERIODS.items():
        scenarios_menu_items = []

        for scenario in scenarios:
            if scenario == "overview":
                url = reverse("frontend:period", args=[period])
            else:
                url = reverse("frontend:scenario", args=[period, scenario])

            scenarios_menu_items.append(
                {
                    "id": scenario,
                    "name": scenario.title().replace("_", " "),
                    "url": url,
                }
            )

        url = reverse("frontend:period", args=[period])
        if current_scenario in scenarios and current_period != period:
            # The current view has an equivalent page for the other period.
            # Instead of using the "overview" as the first page for this period
            # use the same scenario.
            url = reverse("frontend:scenario", args=[period, current_scenario])

        menu_items.append(
            {
                "id": period,
                "url": url,
                "scenarios": scenarios_menu_items,
            }
        )

    return menu_items


def render(request, period, scenario=None):
    """
    Renders the data visualisation template
    for the given allocation period and scenario.
    """

    if scenario is None and period == "compare":
        scenario = "beneficiary_states"
    elif scenario is None:
        scenario = "overview"

    if scenario not in ALLOCATION_PERIODS[period]:
        raise Http404()

    context = {
        "PERIOD": period,
        "SCENARIO": scenario,
    }

    template = "%s.html" % scenario

    return _render(request, template, context)
