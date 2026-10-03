# coding: utf-8
from django.views.decorators.csrf import csrf_exempt

from apps.api.service import mcp_key_service
from apps.api.utils.perm_wrapper import perm
from apps.api.utils.public import log_error
from apps.api.utils.response import api_error, api_success, parse_json


@csrf_exempt
@perm(code=None)
def list_keys(request):
    try:
        datas = mcp_key_service.list_keys(request.xxgcms_user)
        return api_success(datas=datas)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def create_key(request):
    try:
        req = parse_json(request)
        data = mcp_key_service.create_key(
            request.xxgcms_user,
            req.get('name', ''),
            req.get('site_id'),
        )
        return api_success(data=data)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def revoke_key(request):
    try:
        req = parse_json(request)
        ret = mcp_key_service.revoke_key(request.xxgcms_user, req.get('id'))
        return api_success(ret=ret)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))
