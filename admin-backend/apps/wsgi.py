"""WSGI entry for 小西瓜CMS backend."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.settings.prod')

application = get_wsgi_application()
