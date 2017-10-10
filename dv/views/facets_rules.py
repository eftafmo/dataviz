from collections import OrderedDict

BASE_FACETS = [
    ('financial_mechanism_ss', 'AND'),
    ('state_name', 'OR'),
    ('priority_sector_ss', 'OR'),
    ('programme_area_ss', 'AND'),
    ('programme_name', 'OR'),
]

PROGRAMME_CUSTOM_FACETS = [
    ('programme_status', 'AND'),
    ('outcome_ss', 'AND'),
]

PROJECT_CUSTOM_FACETS = [
    ('programme_status', 'AND'),
    ('outcome_ss', 'AND'),
    ('project_status', 'AND'),
    ('theme_ss', 'AND'),
    ('geotarget', 'AND'),
]

ORGANISATION_CUSTOM_FACETS = [
    ('project_name', 'AND'),
    ('role_ss', 'AND'),
    ('country', 'AND'),
    ('city', 'AND'),
    ('geotarget', 'AND'),
    ('org_type_category', 'AND'),
    ('org_type', 'AND'),
]

PROGRAMME_FACETS = OrderedDict(BASE_FACETS + PROGRAMME_CUSTOM_FACETS)
PROJECT_FACETS = OrderedDict(BASE_FACETS + PROJECT_CUSTOM_FACETS)
ORGANISATION_FACETS = OrderedDict(BASE_FACETS + ORGANISATION_CUSTOM_FACETS)
NEWS_FACETS = OrderedDict(PROJECT_FACETS)
