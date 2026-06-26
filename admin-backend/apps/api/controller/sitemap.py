# coding: utf-8
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.api.utils.sitemap_tasks import create_sitemaps


@csrf_exempt
def create_sitemap(request):
    create_sitemaps()
    res = {}
    return JsonResponse(res)