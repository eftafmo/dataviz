"""
Django settings for dv project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from django.core.exceptions import ImproperlyConfigured

import environ

env = environ.Env(
    DEBUG=(bool, False),
)  # set default values and casting

# project's base directory (the repo root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# root directory, where project is deployed
ROOT_DIR = os.path.dirname(BASE_DIR)

DB_PATH = env(
    "DJANGO_DB_PATH",
    default=os.path.join(os.path.join(os.path.dirname(BASE_DIR), "db"), "eeag.sqlite3"),
)

# more useful dirs:
# the web server's vhost root
WEBROOT_DIR = os.path.join(ROOT_DIR, "webroot")
# where asset bundling happens
BUILD_DIR = os.path.join(ROOT_DIR, "build")

# TODO: handle this nicely
DEBUG = bool(os.environ.get("DEBUG"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# Application definition

INSTALLED_APPS = [
    # The django-material theme breaks ck editor.
    # 'material',
    # 'material.admin',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.humanize",
    "django_countries",
    "haystack",
    "rest_framework",
    "dv",
    "ckeditor",
    "django.contrib.staticfiles",
]

REST_FRAMEWORK = {
    # 'DEFAULT_PAGINATION_CLASS': (
    #     'rest_framework.pagination.CursorPagination',
    # ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "dv.middleware.CORSMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
]

ROOT_URLCONF = "dv.urls"
# Why fonts need CORS?
CORS_ALLOW_PATHS = ("/api/", "/assets/data/", "/assets/fonts/")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "dv.context.get_context",
            ],
        },
    },
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
    },
]

WSGI_APPLICATION = "dv.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
STATIC_URL = "/assets/"
STATIC_ROOT = os.path.join(WEBROOT_DIR, "static")
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "assets"),
    # include the bundle dir
    os.path.join(BUILD_DIR, "assets"),
)

CKEDITOR_JQUERY_URL = "https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js"

CKEDITOR_CONFIGS = {
    "default": {
        "toolbar_bdr": [
            [
                "Format",
                "Bold",
                "Italic",
                "Underline",
                "Strike",
                "Subscript",
                "Superscript",
                "-",
                "Undo",
                "Redo",
                "RemoveFormat",
            ],
            [
                "NumberedList",
                "BulletedList",
                "-",
                "Outdent",
                "Indent",
                "Blockquote",
                "-",
                "JustifyLeft",
                "JustifyCenter",
                "JustifyRight",
                "JustifyBlock",
            ],
            ["Link", "Unlink", "Anchor"],
            ["Image", "Flash", "Table", "Smiley", "SpecialChar", "HorizontalRule"],
            ["TextColor", "BGColor"],
            ["Maximize", "ShowBlocks", "-", "Source"],
        ],
        "toolbar": "bdr",
        "width": "100%",
    },
}

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "dv.lib.es7.CustomES7SearchEngine",
        "URL": "http://127.0.0.1:9200/",
        "INDEX_NAME": "eeagrants",
        "SILENTLY_FAIL": False,
        "TIMEOUT": env("HAYSTACK_TIMEOUT", cast=int, default=60),
    },
}

# Caching system

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/var/tmp/django_cache",
    }
}

API_CACHE_SECONDS = 60 * 60 * 24  # 1 day

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

try:
    # this is stupid, the settings file is no place for startup code
    SENTRY_DSN = env("SENTRY_DSN")
    SENTRY_ENVIRONMENT = env("SENTRY_ENVIRONMENT")
except ImproperlyConfigured:
    pass
else:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
    )

from .localsettings import *  # noqa: E402, F401, F403
