# coding: utf-8
from django.views.decorators.csrf import csrf_exempt

from apps.api.service import link_service
from apps.api.utils.perm_wrapper import perm
from apps.api.utils.public import log_error
from apps.api.utils.response import api_error, api_success, parse_json
from apps.api.utils.upload import validate_image_ext


@csrf_exempt
@perm(code=None)
def get_link_list(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        page_num = req.get('page_num')
        page_size = req.get('page_size')
        start_page = (page_num - 1) * page_size
        datas, total_count = link_service.get_link_list(domain, start_page, page_size)
        return api_success(data=datas, total_count=total_count)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def upload_link_pic(request):
    try:
        ext_name = validate_image_ext(request.FILES['file'].name.split('.')[-1])
        data = link_service.upload_link_pic(request.FILES['file'], ext_name)
        return api_success(data=data)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def add_link(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        name = req.get('name', '')
        if link_service.check_name(domain, name):
            raise Exception('该名称已存在')
        ret = link_service.add_link(domain, req)
        return api_success(ret=ret)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def update_link(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        link_id = req.get('id')
        name = req.get('name')
        id2 = link_service.get_id_by_name(domain, name)
        if id2 and link_id != id2:
            raise Exception('该名称已存在')
        ret = link_service.update_link(domain, link_id, req)
        return api_success(ret=ret)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def del_link(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        link_id = req.get('id')
        ret = link_service.del_link(domain, link_id)
        return api_success(ret=ret)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))
