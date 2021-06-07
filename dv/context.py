from django.conf import settings
from dv.lib.assets import load_manifest
from dv.views.dataviz import get_menu


def get_context(request):
    # expose public settings
    expose_settings = [
        'DEBUG',
        'SENTRY_DSN', 'SENTRY_ENVIRONMENT',
    ]
    if not settings.DEBUG:
        expose_settings += ['GOOGLE_ANALYTICS_PROPERTY_ID']

    exposed_settings = {
        s: getattr(settings, s, None)
        for s in expose_settings}

    out = exposed_settings
    out['settings'] = exposed_settings.copy()

    # add assets
    try:
        assets = load_manifest()
    except FileNotFoundError:
        if settings.DEBUG:
            assets = {}
        else:
            raise
    out['assets'] = assets

    # constants
    out['MENU'] = get_menu()

    return out
