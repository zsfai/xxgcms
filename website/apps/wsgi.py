"""
WSGI config for website project.
"""
import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application

website_root = Path(__file__).resolve().parent.parent
admin_root = website_root.parent / 'admin-backend'

from apps.utils.env_bootstrap import bootstrap_website_env

bootstrap_website_env(
    website_root,
    admin_root if admin_root.is_dir() else None,
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.settings.prod')

application = get_wsgi_application()
