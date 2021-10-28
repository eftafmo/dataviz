import environ

try:
    BASE_DIR, INSTALLED_APPS, DB_PATH
except NameError:
    from .settings import BASE_DIR, INSTALLED_APPS, DB_PATH  # noqa: F401

root = environ.Path(__file__) - 3  # three folder back (/a/b/c/ - 3 = /)
env = environ.Env(
    DEBUG=(bool, False),
)  # set default values and casting

DEBUG = env("DEBUG", False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
SECRET_KEY = env("SECRET_KEY")
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DB_PATH,
    }
}


HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "dv.lib.es7.CustomES7SearchEngine",
        "URL": "http://elasticsearch:9200/",
        "INDEX_NAME": "eeagrants",
        "SILENTLY_FAIL": False,
        "TIMEOUT": env("HAYSTACK_TIMEOUT", cast=int, default=60),
    },
}

GOOGLE_ANALYTICS_PROPERTY_ID = env("GOOGLE_ANALYTICS_PROPERTY_ID")

MSSQL_SERVER = env("MSSQL_SERVER", default="")
MSSQL_USERNAME = env("MSSQL_USERNAME", default="")
MSSQL_PASSWORD = env("MSSQL_PASSWORD", default="")
MSSQL_DATABASE = env("MSSQL_DATABASE", default="")


# CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = (,)

# TODO: logging
# TODO: more production settings (./manage.py check --deploy)
