# coding: utf-8
from django.views.decorators.csrf import csrf_exempt

from apps.api.service import media_service
from apps.api.utils.perm_wrapper import perm
from apps.api.utils.public import log_error
from apps.api.utils.response import api_error, api_success, parse_json


@csrf_exempt
@perm(code=None)
def get_media_list(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        page_num = int(req.get('page_num') or 1)
        page_size = int(req.get('page_size') or 20)
        if page_num < 1:
            page_num = 1
        if page_size < 1:
            page_size = 20
        start_page = (page_num - 1) * page_size
        file_type = req.get('file_type') or ''
        keyword = req.get('keyword') or ''
        datas, total_count = media_service.get_media_list(
            domain, start_page, page_size, file_type=file_type, keyword=keyword,
        )
        return api_success(datas=datas, total_count=total_count)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def upload_media(request):
    try:
        domain = request.META.get('HTTP_DOMAIN') or request.POST.get('domain', '')
        if not domain:
            raise ValueError('请先选择站点')
        if 'file' not in request.FILES:
            raise ValueError('请选择要上传的文件')
        data = media_service.upload_media(domain, request.FILES['file'])
        return api_success(data=data)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def rename_media(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        media_id = req.get('id')
        name = req.get('name', '')
        if not media_id:
            raise ValueError('缺少文件 id')
        ret = media_service.rename_media(domain, media_id, name)
        return api_success(ret=ret)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def del_media(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        media_id = req.get('id')
        if not media_id:
            raise ValueError('缺少文件 id')
        ret = media_service.del_media(domain, media_id)
        return api_success(ret=ret)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))
