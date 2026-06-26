# coding: utf-8
"""Shared Django settings for website frontend."""
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PROJECT_DIR, 'apps'))

_env_file = os.path.join(PROJECT_DIR, '.env')
if os.path.isfile(_env_file):
    with open(_env_file, encoding='utf-8') as _f:
        for _line in _f:
            _line = _line.strip()
            if not _line or _line.startswith('#') or '=' not in _line:
                continue
            _key, _val = _line.split('=', 1)
            os.environ[_key.strip()] = _val.strip()

BASE_DIR = PROJECT_DIR


def require_env(name):
    value = os.environ.get(name, '').strip()
    if not value:
        raise RuntimeError(
            f'环境变量 {name} 未设置。请在 admin-backend 运行 python manage.py setup，'
            f'或在本目录配置 .env'
        )
    return value


EXPIRES_TIME = int(os.environ.get('XXGCMS_TOKEN_EXPIRES', '7200'))
EXPIRES_TIME_FOR_USER = int(os.environ.get('XXGCMS_USER_TOKEN_EXPIRES', str(30 * 24 * 3600)))

XXGCMS_DB = {
    'host': os.environ.get('XXGCMS_DB_HOST', '127.0.0.1'),
    'port': int(os.environ.get('XXGCMS_DB_PORT', '3306')),
    'user': os.environ.get('XXGCMS_DB_USER', 'root'),
    'password': os.environ.get('XXGCMS_DB_PASSWORD', ''),
    'database': os.environ.get('XXGCMS_DB_NAME', 'xxgcms'),
}

INSTALLED_APPS = [
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'apps.urls'
WSGI_APPLICATION = 'apps.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (os.path.join(BASE_DIR, 'templates'),),
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

DATABASES = {}

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

MEDIA_URL = os.environ.get('WEBSITE_MEDIA_URL', 'http://127.0.0.1:8088/media/')


def _resolve_media_root():
    """与 admin-backend 共用上传目录（xxgcms_static_files）。"""
    media_dir = os.environ.get('XXGCMS_MEDIA_DIR', 'xxgcms_static_files')
    if os.path.isabs(media_dir):
        return media_dir
    admin_media = os.path.join(os.path.dirname(BASE_DIR), 'admin-backend', media_dir)
    if os.path.isdir(admin_media):
        return admin_media
    return os.path.join(BASE_DIR, 'media')


MEDIA_ROOT = _resolve_media_root()

LOG_FORMAT = (
    '%(levelname)s %(asctime)s [%(filename)s:%(lineno)d] '
    '[%(module)s:%(funcName)s] [%(levelname)s]- %(message)s'
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {'format': LOG_FORMAT},
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'console': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'error': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
