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
