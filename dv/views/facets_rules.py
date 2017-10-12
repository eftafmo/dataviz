from collections import OrderedDict

BASE_FACETS = [
    ('financial_mechanism_ss', 'AND'),
    ('state_name', 'OR'),
    ('priority_sector_ss', 'OR'),
    ('programme_area_ss', 'OR'),
    ('programme_name', 'OR'),
]

PROGRAMME_CUSTOM_FACETS = [
    ('programme_status', 'OR'),
    ('outcome_ss', 'OR'),
]

PROJECT_CUSTOM_FACETS = [
    ('programme_status', 'OR'),
    ('outcome_ss', 'OR'),
    ('project_status', 'OR'),
    ('theme_ss', 'OR'),
    ('geotarget', 'OR'),
]

ORGANISATION_CUSTOM_FACETS = [
    ('financial_mechanism_ss', 'AND'),
    ('role_ss', 'OR'),
    ('state_name', 'OR'),
    ('priority_sector_ss', 'OR'),
    ('programme_area_ss', 'OR'),
    ('programme_name', 'OR'),
    ('project_name', 'OR'),
    ('country', 'OR'),
    ('city', 'OR'),
    ('geotarget', 'OR'),
    ('org_type_category', 'OR'),
    ('org_type', 'OR'),
]

PROGRAMME_FACETS = OrderedDict(BASE_FACETS + PROGRAMME_CUSTOM_FACETS)
PROJECT_FACETS = OrderedDict(BASE_FACETS + PROJECT_CUSTOM_FACETS)
ORGANISATION_FACETS = OrderedDict(ORGANISATION_CUSTOM_FACETS)
NEWS_FACETS = OrderedDict(PROJECT_FACETS)

FACET_MIN_COUNT = 1
FACET_LIMIT = 10000
FACET_SORT = 'index'
