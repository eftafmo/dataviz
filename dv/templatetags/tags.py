import re
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_text

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


@register.assignment_tag
def build_filter_template(filter):
    if filter:
        return "search/filters/{}.html".format(filter)
    return ''


@register.assignment_tag
def active(expected_kind, current_kind):
    return 'active' if expected_kind == current_kind else ''


@register.assignment_tag
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
