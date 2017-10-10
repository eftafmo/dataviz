BASE_FACETS = {
    'state_name': 'OR',
    'programme_area_ss': 'AND',
    'priority_sector_ss': 'OR',
    'financial_mechanism_ss': 'AND',
    'programme_name': 'OR',
}

PROGRAMME_CUSTOM_FACETS = {
    'programme_status': 'AND',
    'outcome_ss': 'AND'
}

PROJECT_CUSTOM_FACETS = {
    'programme_status': 'AND',
    'outcome_ss': 'AND',
    'project_status': 'AND',
    'geotarget': 'AND',
    'theme_ss': 'AND',
}

ORGANISATION_CUSTOM_FACETS = {
    'project_name': 'AND',
    'country': 'AND',
    'city': 'AND',
    'geotarget': 'AND',
    'org_type_category': 'AND',
    'org_type': 'AND',
    'role_ss': 'AND',
}

PROGRAMME_FACETS = {**BASE_FACETS, **PROGRAMME_CUSTOM_FACETS}
PROJECT_FACETS = {**BASE_FACETS, **PROJECT_CUSTOM_FACETS}
ORGANISATION_FACETS = {**BASE_FACETS, **ORGANISATION_CUSTOM_FACETS}
NEWS_FACETS = {**PROJECT_FACETS}
