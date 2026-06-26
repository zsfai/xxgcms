# coding: utf-8
import os

from django.urls import include, re_path
from django.views.static import serve

from apps.settings import MEDIA_ROOT
from apps.settings.base import BASE_DIR

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': os.path.join(BASE_DIR, 'static')}),
    re_path(r'', include('pages.urls')),
    re_path(r'', include('pages_en.urls')),
]
