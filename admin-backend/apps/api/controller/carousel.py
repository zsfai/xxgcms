# coding: utf-8
from django.views.decorators.csrf import csrf_exempt

from apps.api.service import carousel_service
from apps.api.utils.perm_wrapper import perm
from apps.api.utils.public import log_error
from apps.api.utils.response import api_error, api_success, parse_json
from apps.api.utils.upload import validate_image_ext


@csrf_exempt
@perm(code=None)
def get_carousel_list(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        page_num = req.get('page_num')
        page_size = req.get('page_size')
        start_page = (page_num - 1) * page_size
        datas, total_count = carousel_service.get_carousel_list(domain, start_page, page_size)
        return api_success(data=datas, total_count=total_count)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def upload_carousel_pic(request):
    try:
        ext_name = validate_image_ext(request.FILES['file'].name.split('.')[-1])
        data = carousel_service.upload_carousel_pic(request.FILES['file'], ext_name)
        return api_success(data=data)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def add_carousel(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        title = req.get('title', '')
        if carousel_service.check_title(domain, title):
            raise Exception('该标题已存在')
        ret = carousel_service.add_carousel(domain, req)
        return api_success(ret=ret)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def update_carousel(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        carousel_id = req.get('id')
        title = req.get('title')
        id2 = carousel_service.get_id_by_title(domain, title)
        if id2 and carousel_id != id2:
            raise Exception('该标题已存在')
        ret = carousel_service.update_carousel(domain, carousel_id, req)
        return api_success(ret=ret)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def del_carousel(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        carousel_id = req.get('id')
        ret = carousel_service.del_carousel(domain, carousel_id)
        return api_success(ret=ret)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def view_carousels(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        datas = carousel_service.view_carousels(domain)
        return api_success(data=datas)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))
