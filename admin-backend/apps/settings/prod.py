# coding: utf-8
import os

from apps.settings.base import *  # noqa: F401,F403

SECRET_KEY = require_env('XXGCMS_SECRET_KEY')
AUTH_SALT = require_env('XXGCMS_AUTH_SALT')

XXGCMS_DB = {
    'host': os.environ.get('XXGCMS_DB_HOST', '127.0.0.1'),
    'port': int(os.environ.get('XXGCMS_DB_PORT', '3306')),
    'user': os.environ.get('XXGCMS_DB_USER', 'root'),
    'password': require_env('XXGCMS_DB_PASSWORD'),
    'database': os.environ.get('XXGCMS_DB_NAME', 'xxgcms'),
}

DEBUG = False
IS_TEST = False
ALLOWED_HOSTS = os.environ.get('XXGCMS_ALLOWED_HOSTS', '*').split(',')

CRONJOBS = [
    ('* * */7 * *', 'apps.api.utils.sitemap_tasks.create_sitemaps'),
]

_log_dir = os.environ.get('XXGCMS_LOG_DIR', '/var/log/xxgcms')
LOGGING['handlers']['file'] = {
    'level': 'DEBUG',
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': os.path.join(_log_dir, 'debug.log'),
    'maxBytes': 1024 * 1024 * 20,
    'backupCount': 3,
    'formatter': 'standard',
}
LOGGING['handlers']['error_file'] = {
    'level': 'ERROR',
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': os.path.join(_log_dir, 'error.log'),
    'maxBytes': 1024 * 1024 * 20,
    'backupCount': 3,
    'formatter': 'standard',
}
LOGGING['loggers']['xxgcms']['handlers'] = ['file', 'console']
LOGGING['loggers']['xxgcms.error']['handlers'] = ['error_file', 'console']
