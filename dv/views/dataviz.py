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


def get_seo_context(request, title="", description=""):
    result = {
        "title": "EEA and Norway Grants",
        "description": "Working together for a green, democratic and resilient Europe",
        "keywords": "",
        "keywords_list": [],
        "full_url": request.build_absolute_uri(request.path),
        "domain": request.get_host(),
        "img": {
            "full_url": request.build_absolute_uri("/assets/imgs/eeaglogo.png"),
            "width": 715,
            "height": 294,
        },
    }
    if title:
        result["title"] += f"- {title}"
    if description:
        result["description"] = description
    return result


TITLES = {
    "overview": "",
    "funding": "Our Grants",
    "cooperation": "Our Partners",
    "projects": "Our Projects",
    "global_goals": "Global Goals",
    "beneficiary_states": "Compare funding by beneficiary states",
    "sectors": "Compare funding by sectors",
}
DESCRIPTIONS = {
    "overview": "",
    "funding": (
        "Learn more about allocations to the Beneficiary States and priority "
        "sectors."
    ),
    "cooperation": (
        "Partnerships are at the centre of the EEA and Norway Grants. "
        "Discover our partnership network."
    ),
    "projects": (
        "Discover projects and initiatives, helping reduce social and "
        "economic disparities and strengthen bilateral relations."
    ),
    "global_goals": (
        "The United Nations’ Sustainable Development Goals reflect a "
        "shared global vision for a peaceful and prosperous world through "
        "sustainable and fair development."
    ),
    "beneficiary_states": (
        "Compare funding periods allocation by financial mechanism "
        "and beneficiary state"
    ),
    "sectors": "Compare funding periods allocation by sectors",
}


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

    template = "%s.html" % scenario
    return _render(
        request,
        template,
        {
            "PERIOD": period,
            "SCENARIO": scenario,
            "seo": get_seo_context(
                request, title=TITLES[scenario], description=DESCRIPTIONS[scenario]
            ),
        },
    )
