from django.conf import settings


def get_context(request):
    expose_settings = ['SENTRY_DSN', 'SENTRY_ENVIRONMENT']
    if not settings.DEBUG:
        expose_settings = ['GOOGLE_ANALYTICS_PROPERTY_ID']

    exposed_settings = {
        s: getattr(settings, s, None)
        for s in expose_settings}

    out = exposed_settings
    out['settings'] = exposed_settings.copy()

    return out
