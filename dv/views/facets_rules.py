from collections import OrderedDict, defaultdict

from dv.lib.utils import FM_DICT
from dv.models import (
    ProgrammeArea,
    State,
)

BASE_FACETS = [
    ("financial_mechanism_ss", "AND"),
    ("period", "OR"),
    ("state_name", "OR"),
    ("priority_sector_ss", "OR"),
    ("programme_area_ss", "OR"),
    ("programme_name", "OR"),
]

BILATERAL_INITIATIVE_CUSTOM_FACETS = [
    ("status", "OR"),
    ("level", "OR"),
]

PROGRAMME_CUSTOM_FACETS = [
    ("programme_status", "OR"),
    ("outcome_ss", "OR"),
    ("organisation", "OR"),
]

PROJECT_CUSTOM_FACETS = [
    ("programme_status", "OR"),
    ("outcome_ss", "OR"),
    ("project_status", "OR"),
    ("theme_ss", "OR"),
    ("geotarget", "OR"),
    ("organisation", "OR"),
]

ORGANISATION_CUSTOM_FACETS = [
    ("financial_mechanism_ss", "AND"),
    ("period", "OR"),
    ("role_ss", "OR"),
    ("state_name", "OR"),
    ("priority_sector_ss", "OR"),
    ("programme_area_ss", "OR"),
    ("programme_name", "OR"),
    ("project_name", "OR"),
    ("country", "OR"),
    ("city", "OR"),
    ("geotarget", "OR"),
    ("org_type_category", "OR"),
    ("org_type", "OR"),
]

NEWS_CUSTOM_FACETS = [
    ("programme_status", "OR"),
    ("outcome_ss", "OR"),
    ("project_name", "OR"),
    ("project_status", "OR"),
    ("theme_ss", "OR"),
    ("geotarget", "OR"),
]

BILATERAL_INITIATIVE_FACETS = OrderedDict(BASE_FACETS + BILATERAL_INITIATIVE_CUSTOM_FACETS)
PROGRAMME_FACETS = OrderedDict(BASE_FACETS + PROGRAMME_CUSTOM_FACETS)
PROJECT_FACETS = OrderedDict(BASE_FACETS + PROJECT_CUSTOM_FACETS)
ORGANISATION_FACETS = OrderedDict(ORGANISATION_CUSTOM_FACETS)
NEWS_FACETS = OrderedDict(BASE_FACETS + NEWS_CUSTOM_FACETS)


def state_name_to_code(state_name):
    ModelFacetRules.init_reordering_rules()
    return ModelFacetRules.STATES_BY_NAME[state_name]


def area_name_to_sector(area_name):
    ModelFacetRules.init_reordering_rules()
    # one area can have multiple sectors, just pick the first
    return next(iter(ModelFacetRules.AREAS_SECTORS[area_name]))


def geotarget_to_nuts(geotarget):
    # See search_indexes.prepare_geotarget
    return geotarget.split(":")[0]


def geotarget_to_state(geotarget):
    return geotarget[0:2]


FACET_TO_FILTERS = {
    "grants": {
        "financial_mechanism_ss": [("fm", None)],
        "state_name": [("beneficiary", state_name_to_code)],  # state code
        "priority_sector_ss": [("sector", None)],
        "programme_area_ss": [("area", None), ("sector", area_name_to_sector)],
    }
}
FACET_TO_FILTERS["partners"] = dict(FACET_TO_FILTERS["grants"])
FACET_TO_FILTERS["projects"] = dict(FACET_TO_FILTERS["grants"])
FACET_TO_FILTERS["projects"].update(
    {
        "geotarget": [
            ("region", geotarget_to_nuts),
            ("beneficiary", geotarget_to_state),
        ],  # code only
    }
)

PRG_STATUS_SORT = {
    "Implementation": 0,
    "Completed": 1,
    "Closed": 2,
    "Approved": 3,
    "Withdrawn": 4,
    "Returned to po": 5,
}
PRJ_STATUS_SORT = {
    "In Progress": 0,
    "Completed": 1,
    "Non Completed": 2,
    "Terminated": 3,
}

FACET_MIN_COUNT = 1
FACET_LIMIT = 10000
FACET_SORT = "index"

ORG_ROLE_SORT = {
    "National Focal Point": 0,
    "Programme Operator": 1,
    "Donor Programme Partner": 2,
    "Project Promoter": 3,
    "Donor Project Partner": 4,
    "Programme Partner": 5,
    "Project Partner": 6,
}

# Donor States first (incl. France as International), then Beneficiary States
COUNTRY_SORT_BOOST = {
    "Iceland": 0,
    "Liechtenstein": 0,
    "Norway": 0,
    "France": 1,
    "Bulgaria": 2,
    "Cyprus": 2,
    "Czech Republic": 2,
    "Estonia": 2,
    "Greece": 2,
    "Hungary": 2,
    "Latvia": 2,
    "Lithuania": 2,
    "Malta": 2,
    "Poland": 2,
    "Portugal": 2,
    "Romania": 2,
    "Slovakia": 2,
    "Slovenia": 2,
    "Spain": 2,
    "Croatia": 2,
}


class ModelFacetRules:

    REORDER_FACETS = {}
    STATES_BY_NAME = {}

    # dicts for filter_facets
    SECTORS_FMS = {}
    AREAS_FMS = {}
    AREAS_SECTORS = {}

    @classmethod
    def init_reordering_rules(cls):
        if cls.REORDER_FACETS:
            return

        areas_list = ProgrammeArea.objects.order_by("-order").prefetch_related(
            "priority_sector", "allocations"
        )

        # sort by -order because there are some duplicated names
        # so get the first occurrence only
        areas_sort = {}
        sectors_sort = {}
        cls.AREAS_SECTORS = defaultdict(set)
        cls.AREAS_FMS = defaultdict(set)
        cls.SECTORS_FMS = defaultdict(set)
        for area in areas_list:
            areas_sort[area.name] = area.order
            sectors_sort[area.priority_sector.name] = area.order
            fms = [
                FM_DICT[fm_code]
                for fm_code in area.allocations.values_list(
                    "financial_mechanism", flat=True
                ).distinct()
            ]

            cls.AREAS_SECTORS[area.name].add(area.priority_sector.name)
            cls.AREAS_FMS[area.name].union(fms)
            cls.SECTORS_FMS[area.priority_sector.name].union(fms)

        cls.REORDER_FACETS = {
            "programme_status": PRG_STATUS_SORT,
            "project_status": PRJ_STATUS_SORT,
            "programme_area_ss": areas_sort,
            "priority_sector_ss": sectors_sort,
            "role_ss": ORG_ROLE_SORT,
        }
        states = State.objects.exclude(code="IN",).values(
            "code",
            "name",
        )
        cls.STATES_BY_NAME = {state["name"]: state["code"] for state in states}
