import os.path
import environ

try:
    BASE_DIR, INSTALLED_APPS
except NameError:
    from .settings import BASE_DIR, INSTALLED_APPS  # noqa: F401

root = environ.Path(__file__) - 3  # three folder back (/a/b/c/ - 3 = /)
env = environ.Env(DEBUG=(bool, False),)  # set default values and casting

DEBUG = env('DEBUG', False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
SECRET_KEY = env('SECRET_KEY')
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join('/var/local/db/eeag.sqlite3'),
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://solr:8983/solr/eeagrants',
        'BATCH_SIZE': 999,
        'SILENTLY_FAIL': False,
        'TIMEOUT': env("HAYSTACK_SOLR_TIMEOUT", cast=int, default=60),
    },
}

GOOGLE_ANALYTICS_PROPERTY_ID = env('GOOGLE_ANALYTICS_PROPERTY_ID')

# CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = (,)

# TODO: logging
# TODO: more production settings (./manage.py check --deploy)
