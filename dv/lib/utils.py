import random
import re
import time
from binascii import crc32
from collections import Iterable
from django.utils.baseconv import base62


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

def uniq_hash(s):
    """
    Create a short hash from a given string.
    Be warned, this function is a liar: it's not really a hash as it's CRC-based,
    and as such it has a high collision potential!
    """
    if not isinstance(s, bytes):
        s = s.encode('utf-8')
    crc = crc32(s)
    return base62.encode(crc)

def mkrandstr():
    return (
        base62.encode(int(time.time())) +
        base62.encode(random.randint(0, 61))
    )
