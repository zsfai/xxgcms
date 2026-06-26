# coding: utf-8
import os

import pymysql.cursors
import difflib
import re
from apps.utils.public import get_cms_front_db_conf, log_debug, log_error, resolve_site_domains, _resolve_site
from apps.pages.mapper import FArticleMapper


def _fill_parent_cate_info(cate_info, cursor):
    """顶级分类 p_id 为 -1 时无父级，避免查询 id=-1 导致空指针。"""
    if not cate_info:
        return
    p_id = cate_info.get("p_id")
    try:
        p_id_int = int(p_id)
    except (TypeError, ValueError):
        return
    if p_id_int <= 0:
        return
    cursor.execute(FArticleMapper.select_cate_info_by_id(), (p_id_int,))
    p_cate_info = cursor.fetchone()
    if p_cate_info is not None:
        cate_info["p_cate_name_en"] = p_cate_info.get("name_en", "")
        cate_info["p_cate_name"] = p_cate_info.get("name", "")


def get_main_menu(host):
    log_debug("开始获取主菜单列表")
    try:
        db_conf = get_cms_front_db_conf(host)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(FArticleMapper.select_main_menu())
            datas = cursor.fetchall()
            return datas
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_menu_list_by_p_id(host, params):
    log_debug("开始获取主菜单列表")
    try:
        db_conf = get_cms_front_db_conf(host)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            p_cate_id = params.get("p_id", None)
            cursor.execute(FArticleMapper.select_menu_list(), (p_cate_id,))
            datas = cursor.fetchall()
            return datas
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_site_base_info(host):
    log_debug("开始获取站点基本信息")
    default_theme = os.environ.get('XXGCMS_DEFAULT_THEME', 'www_xxg_ai')
    try:
        db_conf = get_cms_front_db_conf(host)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            site_info = None
            for domain in resolve_site_domains(host):
                cursor.execute(FArticleMapper.select_site_base_info(), (domain,))
                site_info = cursor.fetchone()
                if site_info:
                    break
            cursor.execute(FArticleMapper.select_friend_links())
            links = cursor.fetchall()
            if site_info is None:
                site = _resolve_site(host)
                site_info = {
                    'site_name': (site or {}).get('name') or host,
                    'domain': host,
                    'theme_dir': default_theme,
                }
            site_info["links"] = links
            if not site_info.get('theme_dir'):
                site_info['theme_dir'] = default_theme
            return site_info
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_index_article_list(host):
    log_debug("开始获取首页分类文章列表")
    try:
        db_conf = get_cms_front_db_conf(host)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(FArticleMapper.select_cate_list_top_level())
            cates = list(cursor.fetchall())
            for cate in cates:
                p_id = cate.get("id", "")
                cursor.execute(FArticleMapper.select_cate_list_by_p_id(), (p_id,))
                sub_cates = list(cursor.fetchall())
                all_cates = [cate] + sub_cates
                for c in all_cates:
                    cursor.execute(FArticleMapper.select_article_list_by_cate_id(), (c.get("id", ""), 48))
                    articles = list(cursor.fetchall())
                    # 为每篇文章添加父级菜单和子级菜单字段
                    for article in articles:
                        article["p_cate_name_en"] = cate.get("name_en", None)
                        if c is not cate:
                            # 子级菜单
                            article["cate_name_en"] = c.get("name_en", None)
                        else:
                            # 父级菜单
                            pass
                    c["article_list"] = articles
                cate["article_list_temp"] = [article for c in all_cates for article in c.get("article_list", [])]
                cate["article_list"] = cate["article_list_temp"][0:13]
            cate_article_list = [article for c in cates for article in c.get("article_list_temp", [])]
            cate_article_list = sorted(cate_article_list, key=lambda x: x.get("pub_time", ""), reverse=True)
            return cate_article_list, cates
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_swipers(host):
    log_debug("开始获取首页轮播图")
    try:
        db_conf = get_cms_front_db_conf(host)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(FArticleMapper.select_swiper_list())
            swipers = list(cursor.fetchall())
            return swipers
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_article_page_list(cate_name_en, start_page, page_size, host):
    log_debug("开始获取文章列表")
    try:
        db_conf = get_cms_front_db_conf(host)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(FArticleMapper.select_article_page_list(), (cate_name_en, start_page, page_size))
            datas = list(cursor.fetchall())
            cursor.execute(FArticleMapper.select_article_total_count(), (cate_name_en,))
            total_count = cursor.fetchone().get("num", 0)
            for d in datas:
                cursor.execute(FArticleMapper.select_article_kws(), (d.get("id", ""),))
                __kws = list(cursor.fetchall())
                d["kws"] = __kws[0:3]
            cursor.execute(FArticleMapper.select_cate_info_by_name_en(), (cate_name_en,))
            cate_info = cursor.fetchone()
            if cate_info is not None:
                _fill_parent_cate_info(cate_info, cursor)
            cate_kw_list = cate_info.get("kws", "").split(",")
            related_tags, __related_tags = [], []
            for kw in cate_kw_list:
                cursor.execute(FArticleMapper.select_cate_related_kws(), (kw,))
                related_tags = list(cursor.fetchall())
                for t in related_tags:
                    if t not in __related_tags:
                        __related_tags.append(t)
                if len(__related_tags) > 20:
                    break
            related_tags = __related_tags[0:16]
            # 获取类别热门文章
            cate_id = cate_info.get("id", "")
            cursor.execute(FArticleMapper.select_hots_articles(), (cate_id,))
            hots = cursor.fetchall()
            return datas, total_count, cate_info, related_tags, hots
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_page_list(start_page, page_size, host):
    log_debug("开始获取文章列表")
    try:
        db_conf = get_cms_front_db_conf(host)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(FArticleMapper.select_page_list(), (start_page, page_size))
            datas = list(cursor.fetchall())
            cursor.execute(FArticleMapper.select_total_count())
            total_count = cursor.fetchone().get("num", 0)
            return datas, total_count
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


# 判断相似度的方法，用到了difflib库
def get_equal_rate(str1, str2):
    return difflib.SequenceMatcher(None, str1, str2).quick_ratio()


def get_tag_page_list(tname, host):
    log_debug("开始获取标签列表")
    try:
        db_conf = get_cms_front_db_conf(host)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            datas = []
            all_aid_sort, __all_aid_sort, aids_set = [], [], []
            cursor.execute(FArticleMapper.select_kw_by_name(), (tname,))
            kw_data = cursor.fetchone()
            kw = kw_data.get("kw", "")
            tid = kw_data.get("id", -1)
            kw_html = "<span style='color:red;'>" + kw + "</span>"
            # 先通过数据库进行标题模糊匹配，这段匹配数据量大了,Like很慢
            # cursor.execute(FArticleMapper.select_tag_article_by_kw(), ('%' + kw + '%', 10))
            # artilces = cursor.fetchall()
            # if artilces is not None and len(artilces) > 0:
            # for a in artilces:
            # aids_set.append(a.get("id", ""))
            # a["title"] = a.get("title", "").replace(kw, kw_html, 1)
            # datas.append(a)
            # 再去通过文章关键词查询
            cursor.execute(FArticleMapper.select_tag_article_list(), (tid, 25))
            datas_temp = cursor.fetchall()
            if datas_temp is not None:
                for d in datas_temp:
                    title = d.get("title", "")
                    aid = d.get("id", "")
                    weight = get_equal_rate(kw, title)  # 比较匹配度
                    all_aid_sort.append({"id": aid, "weight": weight})
                __all_aid_sort = sorted(all_aid_sort,
                                        key=lambda s_kw: s_kw.get("weight", 0),
                                        reverse=True)
                __all_aid_sort = __all_aid_sort[0:25]
                for i in __all_aid_sort:
                    for d in datas_temp:
                        if i.get("id", -1) == d.get("id", -2) and d.get("id", "") not in aids_set:
                            aids_set.append(d.get("id", ""))
                            d["title_pure"] = d.get("title", "")
                            d["title"] = re.sub(re.escape(kw), kw_html, d.get("title", ""), count=1, flags=re.IGNORECASE)
                            datas.append(d)
            if datas is not None and len(datas) < 25:  # 不够25条，再去查其相关联的kw的文章
                cursor.execute(FArticleMapper.select_r_kw_by_kw_id(), (tid, 20))
                r_kw_datas = cursor.fetchall()
                if r_kw_datas is not None and len(r_kw_datas) > 0:
                    r_kw_ids = (i.get("id", "") for i in r_kw_datas)
                    for kw_id in r_kw_ids:
                        cursor.execute(FArticleMapper.select_tag_article_list(), (kw_id, 10))
                        _datas = list(cursor.fetchall())
                        for d in _datas:
                            if d.get("id", "") not in aids_set:
                                aids_set.append(d.get("id", ""))
                                d["title_pure"] = d.get("title", "")
                                d["title"] = re.sub(re.escape(kw), kw_html, d.get("title", ""), count=1, flags=re.IGNORECASE)
                                datas.append(d)
                        if len(datas) >= 25:
                            break
            if datas is not None and len(datas) < 10:
                cursor.execute(FArticleMapper.select_tag_article_rand(), (20,))
                _datas = list(cursor.fetchall())
                datas = datas + _datas
            for d in datas:
                cursor.execute(FArticleMapper.select_article_kws(), (d.get("id", ""),))
                __kws = list(cursor.fetchall())
                d["kws"] = __kws[1:4]
            # 获取标签信息
            cursor.execute(FArticleMapper.select_tag_info(), (tid,))
            tag_info = cursor.fetchone()
            # 获取标签相关标签
            cursor.execute(FArticleMapper.select_related_tags(), (tid,))
            related_tags = cursor.fetchall()
            _d = sorted(datas, key=lambda article: str(article.get("pub_time", "")), reverse=True)
            latest_pub_time = _d[0:1][0].get("pub_time", "")
            if datas is not None and len(datas) > 0:
                for d in datas:
                    if d.get("p_id", None) is not None:
                        cursor.execute(FArticleMapper.select_cate_info_by_id(), (d.get("p_id", ""),))
                        p_cate_info = cursor.fetchone()
                        if p_cate_info is not None:
                            d["p_cate_name_en"] = p_cate_info.get("name_en", "")
                            d["p_cate_name"] = p_cate_info.get("name", "")
            # datas按照id做一下去重，保留不重复的datas返回
            seen_ids = set()
            unique_datas = []
            for d in datas:
                data_id = d.get("id")
                if data_id not in seen_ids:
                    seen_ids.add(data_id)
                    unique_datas.append(d)
            datas = unique_datas
            return datas, tag_info, related_tags, latest_pub_time
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_topic_page_list(tid, host):
    log_debug("开始获取标签列表")
    try:
        db_conf = get_cms_front_db_conf(host)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            datas = []
            all_aid_sort, __all_aid_sort, aids_set = [], [], []
            cursor.execute(FArticleMapper.select_kw_by_id(), (tid,))
            kw_data = cursor.fetchone()
            kw = kw_data.get("kw", "")
            kw_html = "<span style='color:red;'>" + kw + "</span>"
            # 先通过数据库进行标题模糊匹配，这段匹配数据量大了,Like很慢
            # cursor.execute(FArticleMapper.select_tag_article_by_kw(), ('%' + kw + '%', 10))
            # artilces = cursor.fetchall()
            # if artilces is not None and len(artilces) > 0:
            #     for a in artilces:
            #         aids_set.append(a.get("id", ""))
            #         a["title"] = a.get("title", "").replace(kw, kw_html, 1)
            #         datas.append(a)
            # 再去通过文章关键词查询
            cursor.execute(FArticleMapper.select_topic_article_list(), (tid, 40))
            datas_temp = cursor.fetchall()
            if datas_temp is not None:
                for d in datas_temp:
                    title = d.get("title", "")
                    aid = d.get("id", "")
                    weight = get_equal_rate(kw, title)  # 比较匹配度
                    all_aid_sort.append({"id": aid, "weight": weight})
                __all_aid_sort = sorted(all_aid_sort,
                                        key=lambda s_kw: s_kw.get("weight", 0),
                                        reverse=True)
                __all_aid_sort = __all_aid_sort[0:25]
                for i in __all_aid_sort:
                    for d in datas_temp:
                        if i.get("id", -1) == d.get("id", -2) and d.get("id", "") not in aids_set:
                            aids_set.append(d.get("id", ""))
                            d["title"] = d.get("title", "").replace(kw, kw_html, 1)
                            datas.append(d)
            if datas is not None and len(datas) < 25:  # 不够25条，再去查其相关联的kw的文章
                cursor.execute(FArticleMapper.select_r_kw_by_kw_id(), (tid, 20))
                r_kw_datas = cursor.fetchall()
                if r_kw_datas is not None and len(r_kw_datas) > 0:
                    r_kw_ids = (i.get("id", "") for i in r_kw_datas)
                    for kw_id in r_kw_ids:
                        cursor.execute(FArticleMapper.select_topic_article_list(), (kw_id, 10))
                        _datas = list(cursor.fetchall())
                        for d in _datas:
                            if d.get("id", "") not in aids_set:
                                aids_set.append(d.get("id", ""))
                                datas.append(d)
                        if len(datas) >= 25:
                            break
            if datas is not None and len(datas) < 10:
                cursor.execute(FArticleMapper.select_tag_article_rand(), (20,))
                _datas = list(cursor.fetchall())
                datas = datas + _datas
            for d in datas:
                cursor.execute(FArticleMapper.select_article_kws(), (d.get("id", ""),))
                __kws = list(cursor.fetchall())
                d["kws"] = __kws[1:4]
            # 获取标签信息
            cursor.execute(FArticleMapper.select_tag_info(), (tid,))
            tag_info = cursor.fetchone()
            # 获取标签相关标签
            cursor.execute(FArticleMapper.select_related_tags(), (tid,))
            related_tags = cursor.fetchall()
            _d = sorted(datas, key=lambda article: str(article.get("pub_time", "")), reverse=True)
            latest_pub_time = _d[0:1][0].get("pub_time", "")
            return datas, tag_info, related_tags, latest_pub_time
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_source_id_by_slug(slug, host):
    log_debug("开始获取文章ID")
    try:
        db_conf = get_cms_front_db_conf(host)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(FArticleMapper.select_source_id_by_slug(), (slug,))
            data = cursor.fetchone()
            if data is None:
                return None
            else:
                return data.get("source_id", "")
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_article_detail(cate_name_en, source_id, host):
    log_debug("开始获取文章详情")
    try:
        db_conf = get_cms_front_db_conf(host)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            # 获取文章信息
            cursor.execute(FArticleMapper.select_article_by_sid(), (source_id,))
            article_info = cursor.fetchone()
            if article_info is None:
                err_msg = u"%s文章%s不存在" % (host, source_id)
                raise Exception(err_msg)
            # 获取类别信息
            a_id = article_info.get("id", -1)
            cate_id = article_info.get("cate_id", -1)
            cursor.execute(FArticleMapper.select_cate_info(), (cate_id,))
            cate_info = cursor.fetchone()
            if cate_info is not None:
                _fill_parent_cate_info(cate_info, cursor)
            if cate_info is not None and cate_name_en is not None:
                if cate_info.get("name_en", None) != cate_name_en:
                    raise Exception("该栏目不存在")
            # 获取上一篇文章
            cursor.execute(FArticleMapper.select_prev_article(), (a_id, cate_id))
            prev_article = cursor.fetchone()
            if prev_article is not None and cate_info is not None:
                prev_article["p_cate_name_en"] = cate_info.get("p_cate_name_en", "")
                prev_article["p_cate_name"] = cate_info.get("p_cate_name", "")
            # 获取下一篇文章
            cursor.execute(FArticleMapper.select_next_article(), (a_id, cate_id))
            next_article = cursor.fetchone()
            if next_article is not None and cate_info is not None:
                next_article["p_cate_name_en"] = cate_info.get("p_cate_name_en", "")
                next_article["p_cate_name"] = cate_info.get("p_cate_name", "")
            # 获取文章关键词
            cursor.execute(FArticleMapper.select_article_kws(), (a_id,))
            kw_list = list(cursor.fetchall())

            related_tags, __related_tags = [], []
            __related_articles, related_articles = [], []

            if kw_list is not None and len(kw_list) > 0:
                for item in kw_list:
                    # 获取关键词相关联关键词
                    id = item.get("id", None)
                    if id is None:
                        continue
                    else:
                        cursor.execute(FArticleMapper.select_article_related_kws(), (id,))
                        related_tags = list(cursor.fetchall())
                        if related_tags:
                            for t in related_tags:
                                kw = t.get("kw", "")
                                t["kw_slug"] = kw.replace(" ", "-").lower()
                                if t not in __related_tags:
                                    __related_tags.append(t)
                            if len(__related_tags) > 20:
                                break
                related_tags = __related_tags[0:16]
                for item in kw_list:
                    # 获取文章关键词相关文章，用于推荐文章
                    kw = item.get("kw", None)
                    if kw is None:
                        continue
                    else:
                        cursor.execute(FArticleMapper.select_article_by_kw(), (str(kw),))
                        related_articles = list(cursor.fetchall())
                        for r in related_articles:
                            if r not in __related_articles and int(r.get("id", -1)) != int(a_id):
                                __related_articles.append(r)
                        if len(__related_articles) >= 10:
                            break
                related_articles = __related_articles[0:8]
                for r in related_articles:
                    # 根据cate_id查询父级别的分类名称
                    cursor.execute(FArticleMapper.select_cate_info_by_id(), (r.get("p_cate_id", ""),))
                    p_cate_info = cursor.fetchone()
                    if p_cate_info is not None:
                        r["p_cate_name_en"] = p_cate_info.get("name_en", "")
                        r["p_cate_name"] = p_cate_info.get("name", "")
            # 获取类别热门文章
            if cate_id is not None and cate_id != -1:
                cursor.execute(FArticleMapper.select_hots_articles(), (cate_id,))
            else:
                cursor.execute(FArticleMapper.select_lastest_articles())
            hots = cursor.fetchall()
            for h in hots:
                # 根据cate_id查询父级别的分类名称
                cursor.execute(FArticleMapper.select_cate_info_by_id(), (h.get("p_cate_id", ""),))
                p_cate_info = cursor.fetchone()
                if p_cate_info is not None:
                    h["p_cate_name_en"] = p_cate_info.get("name_en", "")
                    h["p_cate_name"] = p_cate_info.get("name", "")

            # 更新浏览次数
            cursor.execute(FArticleMapper.update_view_num(), (a_id,))
            conn.commit()

            return article_info, kw_list, cate_info, prev_article, next_article, related_tags, related_articles, hots
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_lastest_article_page_list(start_page, page_size, host):
    log_debug("开始获取最新的文章列表")
    try:
        db_conf = get_cms_front_db_conf(host)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(FArticleMapper.get_lastest_article_page_list(), (start_page, page_size))
            datas = list(cursor.fetchall())
            return datas
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()