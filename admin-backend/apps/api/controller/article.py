# coding: utf-8
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.api.service import article_service
from apps.api.utils.perm_wrapper import perm
from apps.api.utils.public import log_debug, log_error


@csrf_exempt
@perm(code=None)
def sync_latest_articles(request):
    log_debug("一键同步文章")
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    try:
        ret = article_service.sync_latest_articles(domain)
        res["code"] = 0
        res["ret"] = ret
    except Exception as e:
        log_error("一键同步文章失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def sync_article_info(request):
    log_debug("同步文章信息")
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    sids = req.get("sids", [])
    try:
        ret = article_service.sync_one_article(domain, sids)
        res["code"] = 0
        res["ret"] = ret
    except Exception as e:
        log_error("同步文章失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def del_article_item(request):
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    sids = req.get("sids", [])
    try:
        ret = article_service.del_article_item(domain, sids)
        res["code"] = 0
        res["ret"] = ret
    except Exception as e:
        log_error("删除文章失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def renew_article_item(request):
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    sids = req.get("sids", [])
    try:
        ret = article_service.renew_article_item(domain, sids)
        res["code"] = 0
        res["ret"] = ret
    except Exception as e:
        log_error("恢复文章失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def purge_article_item(request):
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    sids = req.get("sids", [])
    try:
        ret = article_service.purge_article_item(domain, sids)
        res["code"] = 0
        res["ret"] = ret
    except Exception as e:
        log_error("彻底删除文章失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def get_article_list(request):
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    cate_id = req.get("cate_id", -1)
    page_num = req.get("page_num", 0)
    page_size = req.get("page_size", 20)
    ai_only = req.get("ai_only") in (True, 1, '1', 'true', 'Y', 'y')
    try:
        start_page = (page_num - 1) * page_size
        datas, total_count = article_service.get_article_list(
            domain, cate_id, start_page, page_size, ai_only=ai_only,
        )
        res["code"] = 0
        res["datas"] = datas
        res["total_count"] = total_count
    except Exception as e:
        log_error("获取文章列表失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def upload_site_logo_pic(request):
    res, data = {}, None
    try:
        file = request.FILES['file']
        ext_name = str(file.name.split(".")[-1]).lower()
        if ext_name in ('jpg', 'png', 'jpeg', 'gif'):
            data = article_service.upload_site_logo_pic(request.FILES['file'], ext_name)
        else:
            raise Exception("上传的文件不合法")
    except Exception as e:
        log_error("上传图片失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    else:
        res["code"] = 0
        res["data"] = data
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def upload_defaul_pic(request):
    res, data = {}, None
    try:
        file = request.FILES['file']
        ext_name = str(file.name.split(".")[-1]).lower()
        if ext_name in ('jpg', 'png', 'jpeg', 'gif'):
            data = article_service.upload_defaul_pic(request.FILES['file'], ext_name)
        else:
            raise Exception("上传的文件不合法")
    except Exception as e:
        log_error("上传图片失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    else:
        res["code"] = 0
        res["data"] = data
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def get_site_conf(request):
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    try:
        data = article_service.get_site_conf(domain)
        res["code"] = 0
        res["data"] = data
    except Exception as e:
        log_error("获取站点参数配置失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def update_site_conf(request):
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    try:
        ret = article_service.update_site_conf(domain, req)
        res["code"] = 0
        res["ret"] = ret
    except Exception as e:
        log_error("设置参数配置失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def match_article_kws(request):
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    flag = req.get("flag", "")
    try:
        ret = article_service.match_article_kws(domain, flag)
        res["code"] = 0
        res["ret"] = ret
    except Exception as e:
        log_error("一键匹配文章关键词失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def match_some_article_kws(request):
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    sids = req.get("sids", [])
    try:
        ret = article_service.match_some_article_kws(domain, sids)
        res["code"] = 0
        res["ret"] = ret
    except Exception as e:
        log_error("匹配指定文章关键词失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def match_some_kw_kws(request):
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    ids = req.get("ids", [])
    try:
        ret = article_service.match_some_kw_kws(domain, ids)
        res["code"] = 0
        res["ret"] = ret
    except Exception as e:
        log_error("匹配指定关键词关键词失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def update_article_cate(request):
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    cate_id = req.get("cate_id", "")
    aids = req.get("aids", "")
    __aids = aids.split("___")
    try:
        ret = article_service.update_article_cate(domain, cate_id, __aids)
        res["code"] = 0
        res["ret"] = ret
    except Exception as e:
        log_error("操作失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def update_article_pre_pub(request):
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    pre_pub_time = req.get("pre_pub_time", "")
    aids = req.get("aids", "")
    __aids = aids.split("___")
    try:
        ret = article_service.update_article_pre_pub(domain, pre_pub_time, __aids)
        try:
            article_service.make_thumb_pic(domain, __aids)
        except Exception as e:
            log_error("生成缩略图make_thumb_pic出现异常：%s" % str(e))
        res["code"] = 0
        res["ret"] = ret
    except Exception as e:
        log_error("操作失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def match_kw_kws(request):
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    try:
        ret = article_service.match_kw_kws(domain)
        res["code"] = 0
        res["datas"] = ret
    except Exception as e:
        log_error("关键词匹配相关关键词失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def get_cate_list(request):
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    page_num = req.get("page_num")
    page_size = req.get("page_size")
    try:
        start_page = (page_num - 1) * page_size
        datas, total_count = article_service.get_cate_list(domain, start_page, page_size)
        res["code"] = 0
        res["datas"] = datas
        res["total_count"] = total_count
    except Exception as e:
        log_error("获取数据失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def get_article_cate_list(request):
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    try:
        datas = article_service.get_article_cate_list(domain)
        res["code"] = 0
        res["datas"] = datas
    except Exception as e:
        log_error("获取数据失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def upload_cate_pic(request):
    log_debug("上传图片")
    res, data = {}, None
    try:
        file = request.FILES['file']
        ext_name = str(file.name.split(".")[-1]).lower()
        if ext_name in ('jpg', 'png', 'jpeg', 'gif'):
            data = article_service.upload_cate_pic(request.FILES['file'], ext_name)
        else:
            raise Exception("上传的文件不合法")
    except Exception as e:
        log_error("上传图片失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    else:
        res["code"] = 0
        res["data"] = data
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def add_cate(request):
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    name_en = req.get("name_en", "")
    p_id = req.get("p_id", -1)
    ret = False
    try:
        ret = article_service.check_cate_by_name(domain, name_en, p_id)
        if ret is not None:
            raise Exception("该类别英文名称已存在")
        else:
            ret = article_service.add_cate(domain, req)
    except Exception as e:
        log_error("新增失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    else:
        res["code"] = 0
        res["ret"] = ret
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def update_cate(request):
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    name_en = req.get("name_en", "")
    id = req.get("id", "")
    p_id = req.get("p_id", None)
    ret = False
    try:
        check_ret = article_service.check_cate_by_name(domain, name_en, p_id)
        if check_ret is not None:
            __id = check_ret.get("id", "")
            if id != __id:
                raise Exception("该类别英文名称已存在")
            else:
                ret = article_service.update_cate(domain, req)
        else:
            ret = article_service.update_cate(domain, req)
    except Exception as e:
        log_error("更新失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    else:
        res["code"] = 0
        res["ret"] = ret
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def del_cate(request):
    log_debug("删除某个类别")
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    cate_id = req.get("id")
    try:
        ret = article_service.del_cate(domain, cate_id)
        res["code"] = 0
        res["ret"] = ret
    except Exception as e:
        log_error("删除类别失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def make_thumb_pic(request):
    log_debug("生成缩略图:::::make_thumb_pic")
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    try:
        ret = article_service.make_thumb_pic(domain)
        res["code"] = 0
        res["ret"] = ret
    except Exception as e:
        log_error("生成缩略图出现异常：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def hct_auto_post(request):
    log_debug("火车头自动发布文章")
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    cate_id = req.get("cate_id", -1)
    title = req.get("title", "")
    content = req.get("content", "")
    source_url = req.get("source_url", "")
    try:
        ret = article_service.hct_auto_post(domain, cate_id, title, content, source_url)
        res["code"] = 0
        res["ret"] = "发布文章成功：%s" % str(ret)
    except Exception as e:
        log_error("发布文章失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = "发布文章失败：%s" % str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def update_article_desc(request):
    res = {}
    req = json.loads(request.body)
    domain = req.get('domain', '')
    try:
        ret = article_service.update_article_desc(domain)
        res["code"] = 0
        res["ret"] = str(ret)
    except Exception as e:
        log_error("更新文章摘要失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def search_article(request):
    res = {}
    req = json.loads(request.body)
    kw = req.get("keyword", "")
    domain = req.get("domain", "")
    page_num = req.get("page_num")
    page_size = req.get("page_size")
    try:
        start_page = (page_num - 1) * page_size
        datas, total_count = article_service.search_article(domain, kw, start_page, page_size)
        res["code"] = 0
        res["datas"] = datas
        res["total_count"] = total_count
    except Exception as e:
        log_error("搜索文章失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def get_article_detail(request):
    res = {}
    req = json.loads(request.body)
    article_id = req.get("article_id", "")
    domain = req.get("domain", "")
    try:
        data = article_service.get_article_detail(domain, article_id)
        kws = article_service.get_article_kws(domain, article_id)
        res["code"] = 0
        res["data"] = { "info": data, "kws": kws }
    except Exception as e:
        log_error("get_article_detail失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def add_or_update_article(request):
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    article_id = req.get("article_id", -1)
    cate_id = req.get("cate_id", -1)
    title = req.get("title", "")
    slug_url = req.get("slug_url", "")
    show_type = req.get("show_type", 1)
    content = req.get("content", "")
    desc = req.get("desc", "")
    kws = req.get("kws", [])
    pic_url = req.get("pic_url", "")
    publish = req.get("publish") in (True, 1, '1', 'true', 'True', 'Y', 'y')
    try:
        ret = article_service.add_or_update_article(
            domain, article_id, cate_id, title, show_type, content, desc, kws, pic_url, slug_url, publish,
        )
        res["code"] = 0
        res["ret"] = ret
    except Exception as e:
        log_error("发布文章失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = "发布文章失败：%s" % str(e)
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def upload_file(request):
    res, data = {}, None
    domain = request.META.get("HTTP_DOMAIN")
    try:
        file = request.FILES['file']
        ext_name = str(file.name.split(".")[-1]).lower()
        if ext_name in (
            'jpg', 'png', 'jpeg', 'gif', 'bmp', 'webp', 'svg',
            'mp4', 'mp3', 'avi', 'wmv', 'flv', 'mov',
            'mkv', 'webm', 'ogg', 'wav', 'aac',
            'm4a', 'm4v', 'm4b', 'm4p', 'm4r', 'm4w',
            'm4x', 'm4y', 'm4z',
            'zip', 'rar', '7z', 'tar', 'gz'
        ):
            data = article_service.upload_file(domain, request.FILES['file'], ext_name)
        else:
            raise Exception("上传的文件不合法")
    except Exception as e:
        log_error("上传文件失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    else:
        res["code"] = 0
        res["data"] = data
    return JsonResponse(res)


@csrf_exempt
@perm(code=None)
def update_cate_content(request):
    res = {}
    req = json.loads(request.body)
    domain = req.get("domain", "")
    cate_id = req.get("id", "")
    content = req.get("content", "")
    try:
        ret = article_service.update_cate_content(domain, cate_id, content)
        res["code"] = 0
        res["ret"] = ret
    except Exception as e:
        log_error("操作失败：%s" % str(e))
        res["code"] = 10001
        res["message"] = str(e)
    return JsonResponse(res)