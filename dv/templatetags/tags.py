import re
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_text
from django.utils.http import urlencode

from dv.views import frontend as views
from dv.views.facets_rules import FACET_TO_FILTERS

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def currency(value):
    orig = force_text(value)
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>\xa0\g<2>', orig)
    if orig == new:
        return new
    else:
        return currency(new)


@register.filter(is_safe=False)
def sort(value):
    return sorted(value)


@register.filter
def split(value, v):
    return value.split(v)

@register.filter
def value(dict, key):
    return dict[key]

@register.filter
def keyvalue(dict, key):
    try:
        return dict[key]
    except KeyError:
        return ''


@register.filter
def facet_count(facets, facet_name):
    for facet in facets:
        if facet[0] == facet_name:
            return facet[1]
    return ''


@register.simple_tag
def build_filter_template(filter):
    if filter:
        return "search/filters/{}.html".format(filter)
    return ''


@register.simple_tag
def active(expected_kind, current_kind):
    return 'active' if expected_kind == current_kind else ''


@register.simple_tag
def assign(value):
    return value


@register.filter
def kind_label(kind, count):
    kinds = {
        'Programme': ('programme', 'programmes'),
        'Project': ('project', 'projects'),
        'Organisation': ('organisation', 'organisations'),
        'News': ('news', 'project news'),
    }
    return kinds[kind][1 if count > 1 else 0]


@register.filter
def search_view_name(view, view_name):
    if isinstance(view, views.FacetedSearchView):
        return view_name
    scenarios = {
        'frontend:partners': 'frontend:search_organisation',
        'frontend:projects': 'frontend:search_project',
    }
    return scenarios.get(view_name, 'frontend:search_programme')


@register.filter
def scenario_urlparams(facets, scenario):
    #  TODO: there must be a better way to map these
    result = {}
    for f in facets:
        if facets[f] and f in FACET_TO_FILTERS[scenario]:
            rules = FACET_TO_FILTERS[scenario][f]
            for r in rules:
                result[r[0]] = facets[f][0] if not r[1] else r[1](facets[f][0])
    return urlencode(result)


@register.simple_tag
def url_replace(request, field, value):

    dict_ = request.GET.copy()

    dict_[field] = value
    return '?' + dict_.urlencode()
