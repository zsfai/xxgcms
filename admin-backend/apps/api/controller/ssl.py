# coding: utf-8
from django.views.decorators.csrf import csrf_exempt

from apps.api.service import domain_ssl_service
from apps.api.utils.perm_wrapper import perm
from apps.api.utils.public import log_error
from apps.api.utils.response import api_error, api_success, parse_json


def _read_ssl_payload(request):
    if request.FILES.get('fullchain_file') and request.FILES.get('privkey_file'):
        return {
            'site_id': int(request.POST.get('site_id', 0) or 0),
            'domain_aliases': request.POST.get('domain_aliases', ''),
            'ssl_enabled': request.POST.get('ssl_enabled', 'Y'),
            'force_https': request.POST.get('force_https', 'Y'),
            'fullchain_pem': request.FILES['fullchain_file'].read().decode('utf-8', errors='replace'),
            'privkey_pem': request.FILES['privkey_file'].read().decode('utf-8', errors='replace'),
        }
    req = parse_json(request)
    if 'site_id' in req:
        req['site_id'] = int(req.get('site_id') or 0)
    return req


@csrf_exempt
@perm(code=None)
def get_site_ssl(request):
    try:
        req = parse_json(request)
        site_id = int(req.get('site_id') or 0)
        data = domain_ssl_service.get_site_ssl(request.xxgcms_user, site_id)
        return api_success(data=data)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def test_site_ssl(request):
    try:
        req = _read_ssl_payload(request)
        data = domain_ssl_service.test_site_ssl(request.xxgcms_user, req)
        return api_success(data=data, message='证书校验通过')
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def update_site_ssl(request):
    try:
        req = _read_ssl_payload(request)
        data = domain_ssl_service.update_site_ssl(request.xxgcms_user, req)
        return api_success(data=data, message='SSL 配置已保存，预计数秒内生效')
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def sync_nginx(request):
    try:
        count = domain_ssl_service.sync_all_enabled_sites()
        return api_success(data={'count': count}, message=f'已同步 {count} 个站点 Nginx 配置')
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))
