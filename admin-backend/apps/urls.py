# coding:utf-8
from django.urls import include, re_path
from django.views.static import serve
from apps.api.mcp.views import mcp_endpoint
from apps.settings import MEDIA_ROOT


urlpatterns = [
    re_path(r'^api/', include('api.urls')),
    re_path(r'^mcp/?$', mcp_endpoint),
    re_path(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
]
