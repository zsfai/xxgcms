# coding: utf-8
from django.views.decorators.csrf import csrf_exempt

from apps.api.forms import UserForm
from apps.api.service import base_service, token_service
from apps.api.utils.perm_wrapper import perm
from apps.api.utils.public import log_debug, log_error
from apps.api.utils.response import api_error, api_success, parse_json
from apps.api.utils.upload import validate_image_ext


@csrf_exempt
def login(request):
    try:
        req = parse_json(request)
        log_debug(req)
        user_form = UserForm(req)
        if not user_form.is_valid():
            return api_error('存在不合法的输入')
        name = user_form.cleaned_data['name']
        pwd = user_form.cleaned_data['pwd']
        if not base_service.login(name, pwd):
            return api_error('账号和密码有误')
        token = token_service.create_token(name)
        base_service.refesh_site_conf(name)
        return api_success(ret=True, token=token)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def change_password(request):
    try:
        req = parse_json(request)
        ret = base_service.change_password(
            request.xxgcms_user,
            req.get('old_pwd', ''),
            req.get('new_pwd', ''),
        )
        return api_success(ret=ret, message='密码修改成功')
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def refesh_site_conf(request):
    try:
        base_service.refesh_site_conf(request.xxgcms_user)
        return api_success(ret=True)
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def get_site_page_list(request):
    try:
        req = parse_json(request)
        page_num = req.get('page_num')
        page_size = req.get('page_size')
        start_page = (page_num - 1) * page_size
        datas, total_count = base_service.get_site_page_list(
            request.xxgcms_user, start_page, page_size,
        )
        return api_success(datas=datas, total_count=total_count)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def get_site_list(request):
    try:
        datas = base_service.get_site_list(request.xxgcms_user)
        return api_success(datas=datas)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def upload_site_pic(request):
    try:
        ext_name = validate_image_ext(request.FILES['file'].name.split('.')[-1])
        data = base_service.upload_site_pic(request.FILES['file'], ext_name)
        return api_success(data=data)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def test_site_db(request):
    try:
        req = parse_json(request)
        data = base_service.test_site_cms_db(req)
        return api_success(data=data)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def add_site(request):
    try:
        req = parse_json(request)
        name = req.get('name', '')
        root_path = req.get('root_path', '')
        user_name = request.xxgcms_user
        if not (req.get('db_x_name') or '').strip():
            raise Exception('请填写 CMS 数据库名')
        if base_service.select_site_by_name(user_name, name):
            raise Exception('该站点名称已存在')
        if base_service.select_site_by_root_path(user_name, root_path):
            raise Exception('该站点根目录已被其他站点所使用的')
        ret = base_service.add_site(user_name, req)
        return api_success(ret=ret, message='站点创建成功，CMS 数据库表已自动初始化')
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def update_site(request):
    try:
        req = parse_json(request)
        name = req.get('name', '')
        root_path = req.get('root_path', '')
        site_id = req.get('id', -1)
        user_name = request.xxgcms_user
        site = base_service.select_site_by_name(user_name, name)
        if site and site_id != site.get('id', -1):
            raise Exception('该站点名称已存在')
        site = base_service.select_site_by_root_path(user_name, root_path)
        if site and site_id != site.get('id', -1):
            raise Exception('该站点根目录已被其他站点所使用的')
        ret = base_service.update_site(req)
        base_service.refesh_site_conf(user_name)
        return api_success(ret=ret)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def del_site(request):
    try:
        req = parse_json(request)
        site_id = req.get('id')
        ret = base_service.del_site(site_id, request.xxgcms_user)
        return api_success(ret=ret)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))
