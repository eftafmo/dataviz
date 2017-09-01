import os.path
import environ

try:
    BASE_DIR
except NameError:
    from .settings import BASE_DIR

root = environ.Path(__file__) - 3  # three folder back (/a/b/c/ - 3 = /)
env = environ.Env(DEBUG=(bool, False),)  # set default values and casting

DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
SECRET_KEY = env('SECRET_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join('/var/local/db/eeag.sqlite3'),
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://solr:8983/solr/eeagrants'
    },
}

# CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = (,)

# TODO: logging
# TODO: more production settings (./manage.py check --deploy)