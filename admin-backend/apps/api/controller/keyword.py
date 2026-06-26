# coding: utf-8
from django.views.decorators.csrf import csrf_exempt

from apps.api.service import keyword_service
from apps.api.utils.perm_wrapper import perm
from apps.api.utils.public import log_debug, log_error
from apps.api.utils.response import api_error, api_success, parse_json


@csrf_exempt
@perm(code=None)
def upload_excel(request):
    domain = request.META.get('HTTP_DOMAIN')
    try:
        ext_name = request.FILES['file'].name.split('.')[-1].lower()
        if ext_name not in ('xls', 'xlsx'):
            raise Exception('上传的文件不合法')
        add_kw_count = keyword_service.upload_excel(domain, request.FILES['file'], ext_name)
        return api_success(add_kw_count=add_kw_count)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def get_kw_list(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        page_num = req.get('page_num')
        page_size = req.get('page_size')
        start_page = (page_num - 1) * page_size
        datas, total_count = keyword_service.get_kw_list(domain, start_page, page_size)
        return api_success(datas=datas, total_count=total_count)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def del_kw(request):
    log_debug('删除某个关键词')
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        kw_id = req.get('id')
        ret = keyword_service.del_kw(domain, kw_id)
        return api_success(ret=ret)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def add_kw(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        kw = req.get('kw')
        if keyword_service.check_kw(domain, kw):
            raise Exception('该关键词已存在')
        new_kw_id = keyword_service.add_kw(domain, kw)
        return api_success(ret=True, data={'id': new_kw_id})
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def update_kw(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        kw_id = req.get('id')
        kw = req.get('kw')
        if not kw_id:
            raise Exception('缺少关键词 ID')
        ret = keyword_service.update_kw(domain, kw_id, kw)
        return api_success(ret=ret)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def search_kw(request):
    try:
        req = parse_json(request)
        kw = req.get('keyword', '')
        domain = req.get('domain', '')
        page_num = req.get('page_num')
        page_size = req.get('page_size')
        start_page = (page_num - 1) * page_size
        datas, total_count = keyword_service.search_kw(domain, kw, start_page, page_size)
        return api_success(data=datas, total_count=total_count)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))
