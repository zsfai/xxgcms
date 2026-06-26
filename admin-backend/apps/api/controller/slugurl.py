# coding: utf-8
from django.views.decorators.csrf import csrf_exempt

from apps.api.service import slugurl_service
from apps.api.utils.perm_wrapper import perm
from apps.api.utils.public import log_error
from apps.api.utils.response import api_error, api_success, parse_json


@csrf_exempt
@perm(code=None)
def generate_article_slug_url_by_title(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        article_title = req.get('article_title', '')
        data = slugurl_service.generate_article_slug_url_by_title(domain, article_title)
        return api_success(data=data)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))
