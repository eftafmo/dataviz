import re
import six
from collections import Iterable


def camel_case_to__(txt):
    """
    converts underscoreCase to underscore_case
    """
    try:
        cc_re = camel_case_to__._cc_re
    except AttributeError:
        cc_re = camel_case_to__._cc_re = re.compile(
            '((?<=.)[A-Z](?=[a-z0-9])|(?<=[a-z0-9])[A-Z])')

    return re.sub(cc_re, r'_\1', txt).lower()

def str_to_constant_name(txt):
    """
    converts the string to something usable as a constant name
    """
    txt = camel_case_to__(txt)
    txt = re.sub(r'[^\w]', '_', txt)
    txt = re.sub(r'__+', '_', txt)

    return txt.upper()

def is_iter(v):
    """Returns True only for non-string iterables."""
    return not isinstance(v, str) and isinstance(v, Iterable)
