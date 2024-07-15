"""
helper stuff for handling vite manifest
"""

import json
import re
import os.path

# from functools import lru_cache
from django.conf import settings


# TODO: cache in production, don't cache during debug
# @lru_cache(maxsize=None)
def load_manifest():
    manifest = os.path.join(settings.BUILD_DIR, ".vite", "manifest.json")

    _entries = {}
    assets = {}
    deps = set()

    with open(manifest) as mnf:
        _entries = json.load(mnf)

    for k, v in _entries.items():
        if not v.get("isEntry", False):
            continue

        assets[k] = v["file"]
        # add css
        try:
            css = v["css"][0]
        except (KeyError, IndexError):
            pass
        else:
            assets[re.sub(r"\.js$", ".css", k)] = css

        # register deps
        try:
            deps.update(v["imports"])
        except KeyError:
            pass

    # register deps, replace their hash
    for dep in deps:
        asset = _entries[dep]["file"]

        dep = dep.rsplit(".", 2)
        k = f"{dep[0]}.{dep[2]}"

        assets[k] = asset

    return assets
