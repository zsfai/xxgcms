# coding: utf-8
from .base import *  # noqa: F401,F403

SECRET_KEY = require_env('WEBSITE_SECRET_KEY')
AUTH_SALT = os.environ.get('XXGCMS_AUTH_SALT', '')

DEBUG = True
IS_TEST = True
ALLOWED_HOSTS = ['*']

XXGCMS_DB = {
    'host': os.environ.get('XXGCMS_DB_HOST', '127.0.0.1'),
    'port': int(os.environ.get('XXGCMS_DB_PORT', '3306')),
    'user': os.environ.get('XXGCMS_DB_USER', 'root'),
    'password': require_env('XXGCMS_DB_PASSWORD'),
    'database': os.environ.get('XXGCMS_DB_NAME', 'xxgcms'),
}

LOGGING['loggers']['django']['handlers'] = ['console']
LOGGING['loggers']['console']['handlers'] = ['console']
LOGGING['loggers']['error']['handlers'] = ['console']
