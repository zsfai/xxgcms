# coding: utf-8
"""Shared Django settings for 小西瓜CMS backend."""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, os.path.join(PROJECT_DIR, 'apps'))

# 加载项目根目录 .env（覆盖系统环境变量，确保项目配置生效）
_env_file = os.path.join(PROJECT_DIR, '.env')
if os.path.isfile(_env_file):
    with open(_env_file, encoding='utf-8') as _f:
        for _line in _f:
            _line = _line.strip()
            if not _line or _line.startswith('#') or '=' not in _line:
                continue
            _key, _val = _line.split('=', 1)
            os.environ[_key.strip()] = _val.strip()

def require_env(name):
    value = os.environ.get(name, '').strip()
    if not value:
        raise RuntimeError(
            f'环境变量 {name} 未设置。请运行: python manage.py init_env 或 python manage.py setup'
        )
    return value


SECRET_KEY = os.environ.get('XXGCMS_SECRET_KEY', '')
AUTH_SALT = os.environ.get('XXGCMS_AUTH_SALT', '')
EXPIRES_TIME = int(os.environ.get('XXGCMS_TOKEN_EXPIRES', 3600 * 10))
EXPIRES_TIME_FOR_USER = int(os.environ.get('XXGCMS_USER_TOKEN_EXPIRES', 30 * 24 * 3600))

INSTALLED_APPS = [
    'apps.api.apps.ApiConfig',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django_crontab',
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
        'DIRS': [os.path.join(PROJECT_DIR, 'templates')],
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
STATICFILES_DIRS = []
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

MEDIA_ROOT_DIR = os.environ.get('XXGCMS_MEDIA_DIR', 'xxgcms_static_files')
MEDIA_URL = os.environ.get('XXGCMS_MEDIA_URL', 'http://127.0.0.1:8000/media/')
if os.path.isabs(MEDIA_ROOT_DIR):
    MEDIA_ROOT = MEDIA_ROOT_DIR
else:
    MEDIA_ROOT = os.path.join(PROJECT_DIR, MEDIA_ROOT_DIR)

# 小西瓜CMS system database (site registry)
# 原先在 public.py 里按 IS_TEST 切换；现统一走环境变量 / .env
# 开发若连远程库，在 .env 中设置 XXGCMS_DB_HOST=192.168.2.100
XXGCMS_DB = {
    'host': os.environ.get('XXGCMS_DB_HOST', '127.0.0.1'),
    'port': int(os.environ.get('XXGCMS_DB_PORT', '3306')),
    'user': os.environ.get('XXGCMS_DB_USER', 'root'),
    'password': os.environ.get('XXGCMS_DB_PASSWORD', ''),
    'database': os.environ.get('XXGCMS_DB_NAME', 'xxgcms'),
}

LOG_FORMAT = (
    '%(levelname)s %(asctime)s [%(filename)s:%(lineno)d] '
    '[%(module)s:%(funcName)s] %(message)s'
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
        'xxgcms': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'xxgcms.error': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
