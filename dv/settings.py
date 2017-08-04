"""
Django settings for dv project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# project's base directory (the repo root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# root directory, where project is deployed
ROOT_DIR = os.path.dirname(BASE_DIR)

# more useful dirs:
# the web server's vhost root
WEBROOT_DIR = os.path.join(ROOT_DIR, 'webroot')
# used for building webpack bundles for now
BUILD_DIR = os.path.join(ROOT_DIR, 'build')

# TODO: handle this nicely
DEBUG = bool(os.environ.get('DEBUG'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# Application definition

INSTALLED_APPS = [
    'material',
    'material.admin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'haystack',
    'rest_framework',
    'webpack_loader',
    'dv',
    'ckeditor',
]

if not DEBUG:
    # needed in production for collectstatic.
    # on dev the staticfiles view is configured manually in urls,
    # because otherwise this skips middleware.
    INSTALLED_APPS += ['django.contrib.staticfiles']

REST_FRAMEWORK = {
    # 'DEFAULT_PAGINATION_CLASS': (
    #     'rest_framework.pagination.CursorPagination',
    # ),
    'PAGE_SIZE': 10,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'dv.middleware.CORSMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dv.urls'
CORS_ALLOW_PATHS = ('/api/', '/assets/data/')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
    },
]

WSGI_APPLICATION = 'dv.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
STATIC_URL = '/assets/'
STATIC_ROOT = os.path.join(WEBROOT_DIR, 'static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'assets'),
    # include webpack output
    (os.path.join(BUILD_DIR, 'webpack-bundles')),
)

CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js'

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar_bdr': [
            ['Format', 'Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'Undo', 'Redo', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', 'Blockquote', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Flash', 'Table', 'Smiley', 'SpecialChar', 'HorizontalRule'],
            ['TextColor', 'BGColor'],
            ['Maximize', 'ShowBlocks', '-', 'Source'],
        ],
        'toolbar': 'bdr',
        'width': '100%',
    },
}


WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': os.path.join(BUILD_DIR, 'webpack-stats.json'),
        'POLL_INTERVAL': 10,
        'CACHE': not DEBUG,
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://localhost:8983/solr/eeagrants'
    },
}

from .localsettings import *
