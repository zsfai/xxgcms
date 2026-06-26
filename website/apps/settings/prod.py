# coding: utf-8
import os

from .base import *  # noqa: F401,F403

SECRET_KEY = require_env('WEBSITE_SECRET_KEY')
AUTH_SALT = os.environ.get('XXGCMS_AUTH_SALT', '')

DEBUG = False
IS_TEST = False
ALLOWED_HOSTS = os.environ.get('WEBSITE_ALLOWED_HOSTS', '*').split(',')

XXGCMS_DB = {
    'host': os.environ.get('XXGCMS_DB_HOST', '127.0.0.1'),
    'port': int(os.environ.get('XXGCMS_DB_PORT', '3306')),
    'user': os.environ.get('XXGCMS_DB_USER', 'root'),
    'password': require_env('XXGCMS_DB_PASSWORD'),
    'database': os.environ.get('XXGCMS_DB_NAME', 'xxgcms'),
}

_log_dir = os.environ.get('WEBSITE_LOG_DIR', '/var/log/xxgcms')
LOGGING['handlers']['default'] = {
    'level': 'DEBUG',
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': os.path.join(_log_dir, 'debug.log'),
    'maxBytes': 1024 * 1024 * 100,
    'backupCount': 5,
    'formatter': 'standard',
}
LOGGING['handlers']['error'] = {
    'level': 'ERROR',
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': os.path.join(_log_dir, 'error.log'),
    'maxBytes': 1024 * 1024 * 100,
    'backupCount': 5,
    'formatter': 'standard',
}
LOGGING['loggers']['django']['handlers'] = ['default', 'console']
LOGGING['loggers']['console']['handlers'] = ['default', 'console']
LOGGING['loggers']['error']['handlers'] = ['error']
