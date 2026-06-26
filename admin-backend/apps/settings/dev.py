# coding: utf-8
"""开发环境配置。"""
from apps.settings.base import *  # noqa: F401,F403

DEBUG = True
IS_TEST = True
ALLOWED_HOSTS = ['*']

CRONJOBS = []

SECRET_KEY = require_env('XXGCMS_SECRET_KEY')
AUTH_SALT = require_env('XXGCMS_AUTH_SALT')

XXGCMS_DB = {
    'host': os.environ.get('XXGCMS_DB_HOST', '127.0.0.1'),
    'port': int(os.environ.get('XXGCMS_DB_PORT', '3306')),
    'user': os.environ.get('XXGCMS_DB_USER', 'root'),
    'password': require_env('XXGCMS_DB_PASSWORD'),
    'database': os.environ.get('XXGCMS_DB_NAME', 'xxgcms'),
}
