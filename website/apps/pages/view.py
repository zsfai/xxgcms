# coding:utf-8
import arrow
from django.shortcuts import render
from django.http import Http404, HttpResponsePermanentRedirect
from apps.pages.base_conf import PAGE_SIZE
from apps.utils.public import log_debug, log_error
from apps.pages import service


MAX_PAGE_NUM = 10000


def get_page_nav(total_count, page_num, page_size):
    if total_count % page_size == 0:
        total_page = int(total_count / page_size)
    else:
        total_page = int(total_count / page_size) + 1
    has_prev = True if page_num >= 2 else False
    has_next = True if total_page > page_num else False
    curr_page = page_num
    if total_page <= 6:
        start = 1
        end = total_page
    else:
        if curr_page - 3 <= 0:
            end = 6
            start = 1
        else:
            if curr_page + 3 > total_page:
                end = total_page
                start = total_page - 6
            else:
                end = curr_page + 2
                start = curr_page - 3
    return {
        "total_count": total_count,
        "total_page": total_page,
        "curr_page": curr_page,
        "has_next": has_next,
        "has_prev": has_prev,
        "prev_num": page_num - 1 if has_prev is True else 1,
        "next_num": page_num + 1 if has_next is True else total_page,
        "page_range": (i for i in range(start, end + 1))
    }


def index(request):
    host = request.META['HTTP_HOST']
    log_debug("host==================%s" % host)
    p = request.GET.get("p")  # wordpress老url打补丁
    if p is not None:
        return HttpResponsePermanentRedirect("/%s.html" % p)
    main_menu = service.get_main_menu(host)
    site_info = service.get_site_base_info(host)
    cate_article_list, cate_list = service.get_index_article_list(host)
    swipers = service.get_swipers(host)
    theme = site_info.get("theme_dir", "default")
    theme_dir = "default" if (theme is None or theme == "") else theme
    site_info["theme_dir"] = theme_dir
    now = arrow.now()
    num, s_len = 0, 0
    if swipers:
        num = len(swipers)
        if num - 2 <= 0:
            s_len = 1
        else:
            s_len = num - 2
    context = {
        "main_menu": main_menu,
        "site_info": site_info,
        "cate_article_list": cate_article_list,
        "cate_list": cate_list,
        "swipers": swipers[0:s_len],
        "static_pics": swipers[-2:],
        "host": host,
        "links": site_info.get("links", []),
        "date": now.format('YYYY-MM-DD'),
        "time": now.format('HH:mm:ss'),
        "now": now,
        "cate_info": None
    }
    return render(request, '%s/index.html' % theme_dir, context)


def article_list(request, cate_name_en, sub_name=None, page_num=1):
    try:
        host = request.META['HTTP_HOST']
        page_num = int(page_num)
        if page_num > MAX_PAGE_NUM:
            page_num = MAX_PAGE_NUM
        start_page = (page_num - 1) * PAGE_SIZE
        page_size = PAGE_SIZE
        # 如果 sub_name 不为空，则需要根据 cate_name_en 为 sub_name
        cate_name_en = sub_name or cate_name_en
        datas, total_count, cate_info, related_tags, hots = service.get_article_page_list(cate_name_en, start_page,
                                                                                          page_size, host)
        p_id = cate_info.get("p_id", None) if sub_name else cate_info.get("id", None)
        main_menu = service.get_menu_list_by_p_id(host, { "p_id": p_id })
        if main_menu is None or len(main_menu) == 0:
            main_menu = service.get_main_menu(host)
        site_info = service.get_site_base_info(host)
        page_nav = get_page_nav(total_count, page_num, PAGE_SIZE)
        theme = site_info.get("theme_dir", "default")
        theme_dir = "default" if (theme is None or theme == "") else theme
        site_info["theme_dir"] = theme_dir
        context = {
            "main_menu": main_menu,
            "cate_name_en": cate_name_en,
            "article_list": datas,
            "page_nav": page_nav,
            "cate_info": cate_info,
            "related_tags": [
                dict(tag, **{"kw_slug": tag.get("kw_slug", tag.get("kw", "")).replace(" ", "-").lower()})
                for tag in related_tags
            ],
            "hots": hots,
            "site_info": site_info,
            "host": host,
            "links": None
        }
        return render(request, '%s/article_list.html' % theme_dir, context)
    except Exception as e:
        log_error("出现异常：%s" % str(e))
        raise Http404('<h1>Page not found</h1>')


def page_list(request, page_num=1):
    try:
        host = request.META['HTTP_HOST']
        page_num = int(page_num)
        if page_num > MAX_PAGE_NUM:
            raise Exception("已达到最大展示页数")
        start_page = (page_num - 1) * PAGE_SIZE
        page_size = PAGE_SIZE
        datas, total_count = service.get_page_list(start_page, page_size, host)
        main_menu = service.get_main_menu(host)
        site_info = service.get_site_base_info(host)
        page_nav = get_page_nav(total_count, page_num, PAGE_SIZE)
        theme = site_info.get("theme_dir", "default")
        theme_dir = "default" if (theme is None or theme == "") else theme
        site_info["theme_dir"] = theme_dir
        context = {
            "main_menu": main_menu,
            "article_list": datas,
            "page_nav": page_nav,
            "site_info": site_info,
            "related_tags": [],
            "host": host,
            "kws": [],
            "cate_info": None,
            "links": None
        }
        return render(request, '%s/page_list.html' % theme_dir, context)
    except Exception as e:
        log_error("出现异常：%s" % str(e))
        raise Http404('<h1>Page not found</h1>')


def tag_list(request, tname):
    try:
        host = request.META['HTTP_HOST']
        tname = tname.replace("-", " ")
        datas, tag_info, related_tags, latest_pub_time = service.get_tag_page_list(tname, host)
        main_menu = service.get_main_menu(host)
        site_info = service.get_site_base_info(host)
        kws = tag_info.get("kw", "") + "," + ",".join(tag.get("kw", "") for tag in related_tags[0:2])
        theme = site_info.get("theme_dir", "default")
        theme_dir = "default" if (theme is None or theme == "") else theme
        site_info["theme_dir"] = theme_dir
        context = {
            "main_menu": main_menu,
            "article_list": datas,
            "tag_info": tag_info,
            "related_tags": [
                dict(tag, kw_slug=tag.get("kw", "").replace(" ", "-").lower()) for tag in related_tags
            ],
            "latest_pub_time": latest_pub_time,
            "site_info": site_info,
            "host": host,
            "kws": kws,
            "cate_info": None,
            "links": None
        }
        return render(request, '%s/tag_list.html' % theme_dir, context)
    except Exception as e:
        log_error("出现异常：%s" % str(e))
        raise Http404('<h1>Page not found</h1>')


def topic_list(request, tid):
    try:
        host = request.META['HTTP_HOST']
        datas, tag_info, related_tags, latest_pub_time = service.get_topic_page_list(tid, host)
        main_menu = service.get_main_menu(host)
        site_info = service.get_site_base_info(host)
        kws = tag_info.get("kw", "") + "," + ",".join(tag.get("kw", "") for tag in related_tags[0:2])
        theme = site_info.get("theme_dir", "default")
        theme_dir = "default" if (theme is None or theme == "") else theme
        site_info["theme_dir"] = theme_dir
        context = {
            "main_menu": main_menu,
            "article_list": datas,
            "tag_info": tag_info,
            "related_tags": [
                dict(tag, **{"kw_slug": tag.get("kw_slug", tag.get("kw", "")).replace(" ", "-").lower()})
                for tag in related_tags
            ],
            "latest_pub_time": latest_pub_time,
            "site_info": site_info,
            "host": host,
            "kws": kws,
            "cate_info": None,
            "links": None
        }
        return render(request, '%s/tag_list.html' % theme_dir, context)
    except Exception as e:
        log_error("出现异常：%s" % str(e))
        raise Http404('<h1>Page not found</h1>')


def article_detail_by_slug(request, cate_name_en="", sub_name=None, url_path_slug=None):
    try:
        host = request.META['HTTP_HOST']
        source_id = service.get_source_id_by_slug(url_path_slug, host)
        log_debug("source_id======================:::%s" % source_id)
        log_debug("url_path_slug======================:::%s" % url_path_slug)
        if source_id is None:
            raise Http404('<h1>Page not found</h1>')
        return article_detail(request, cate_name_en, sub_name, source_id)
    except Exception as e:
        log_error("出现异常：%s" % str(e))
        raise Http404('<h1>Page not found</h1>')


def article_detail(request, cate_name_en="", sub_name=None, source_id=None):
    try:
        log_debug("cate_name_en======================:::%s" % cate_name_en)
        if cate_name_en == "None":
            raise Http404('<h1>Page not found</h1>')
        host = request.META['HTTP_HOST']
        cate_name_en = sub_name or cate_name_en
        article_info, kw_list, cate_info, prev_article, next_article, related_tags, related_articles, hots = service.get_article_detail(
            cate_name_en, source_id, host)
        if cate_info is not None:
            p_id = cate_info.get("p_id", None) if sub_name else cate_info.get("id", None)
            main_menu = service.get_menu_list_by_p_id(host, { "p_id": p_id })
            if main_menu is None or len(main_menu) == 0:
                main_menu = service.get_main_menu(host)
        else:
            main_menu = service.get_main_menu(host)
        site_info = service.get_site_base_info(host)
        theme = site_info.get("theme_dir", "default")
        theme_dir = "default" if (theme is None or theme == "") else theme
        site_info["theme_dir"] = theme_dir
        kws = ""
        if kw_list is not None and len(kw_list) > 0:
            kw_list = kw_list[0:3]
            kws = ','.join("%s" % i.get("kw", "") for i in kw_list)
        else:
            kw_list = []
        content = article_info.get("content", "")
        from apps.utils.media_urls import fix_content_media_urls
        content = fix_content_media_urls(content, host)
        _related_tags = kw_list + related_tags
        kws2 = []
        for tag in _related_tags:
            kw = tag.get("kw", None)
            if kw in kws2:
                continue
            else:
                kws2.append(kw)
                link = '/topics/%s' % tag.get("kw_slug", "")
                str2 = '<a href="%s" title="%s">%s</a>' % (link, kw, kw)
                if kw is not None:
                    _content, flag = "", 0
                    for line in content.splitlines():
                        if "alt" not in line and kw in line and flag == 0:
                            flag = 1
                            _content = _content + line.replace(kw, str2, 1) + "\n"
                        else:
                            _content = _content + line + "\n"
                    if "alt" not in content and kw in content and flag == 0:
                        content = content.replace(kw, str2, 1)
                    else:
                        content = _content
        content.replace("\r", "")
        strs = ''.join("<p>%s</p>" % line for line in content.splitlines() if line)
        article_info["content"] = strs.replace("<p></p>", "")
        context = {
            "main_menu": main_menu,
            "article_info": article_info,
            "kws": kws,
            "kw_list": kw_list,
            "cate_info": cate_info,
            "prev_article": prev_article,
            "next_article": next_article,
            "related_tags": related_tags,
            "related_articles": related_articles,
            "hots": hots,
            "site_info": site_info,
            "host": host,
            "links": None
        }
        return render(request, '%s/article.html' % theme_dir, context)
    except Exception as e:
        log_error("出现异常：%s" % str(e))
        raise Http404('<h1>Page not found</h1>')