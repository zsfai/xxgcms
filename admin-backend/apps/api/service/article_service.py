# coding: utf-8
import os
import random
import arrow
import difflib
import re
from PIL import Image
import jieba
import requests
from jieba.analyse import extract_tags
from bs4 import BeautifulSoup
import pymysql.cursors
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from apps.api.sql_mapper.slugurl_mapper import SlugurlMapper
from apps.settings import MEDIA_ROOT, MEDIA_ROOT_DIR
from apps.api.utils.base_conf import SITE_MAP
from apps.api.utils.public import get_cms_db_conf, get_cms_x_db_conf, log_debug, log_error, normalize_site_root_path
from apps.api.sql_mapper.article_mapper import ArticleMapper


def sync_latest_articles(site_name):
    log_debug("开始获取文章列表")
    try:
        db_conf = get_cms_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        db_conf2 = get_cms_x_db_conf(site_name)
        conn2 = pymysql.connect(**db_conf2)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            with conn2.cursor() as cursor2:
                conn2.begin()
                cursor.execute(ArticleMapper.select_wp_article_total_count())
                data1 = cursor.fetchone()
                s_total_count = 0 if data1 is None else data1.get("num", 0)
                log_debug("s_total_count:::%s" % s_total_count)
                cursor2.execute(ArticleMapper.select_article_total_count_for_sync_article())
                data2 = cursor2.fetchone()
                total_count = 0 if data2 is None else data2.get("num", 0)
                log_debug("total_count:::%s" % total_count)
                total_count = s_total_count - total_count
                page_size = 20
                times = int(s_total_count / page_size) + 1
                log_debug("times++++++++++++%s" % times)
                for i in range(times):
                    page_start = i * page_size
                    cursor.execute(ArticleMapper.select_wp_article_list2(), (page_start, page_size))
                    datas = cursor.fetchall()
                    for d in datas:
                        source_id = d.get("id", None)
                        source_cate_name = d.get("cate_name", "")
                        cursor2.execute(ArticleMapper.select_article_count_by_sid(), (source_id,))
                        is_exist_data = cursor2.fetchone()
                        if is_exist_data is None or is_exist_data.get("num", 0) == 0:
                            log_debug("该文章不存在====================%s" % source_id)
                            title = d.get("title", "")
                            pub_time = d.get("pubdate", "")
                            content = d.get("content", "")
                            content = re.sub(r'\[caption(.*)"\]', "", content)
                            content = re.sub(r'\[\/caption\]', "", content)
                            soup = BeautifulSoup(content, 'html.parser')
                            desc = soup.get_text()[0:200].replace("\n", "").replace("\r", "")
                            cursor.execute(ArticleMapper.select_wp_article_annex_by_sid(), (source_id,))
                            pic_urls = cursor.fetchall()
                            pic_url = "" if pic_urls is None or len(pic_urls) < 1 else pic_urls[0].get("pic_url", "")
                            cursor2.execute(ArticleMapper.insert_article_sql_sync_latest_articles(),
                                            (title, pub_time, source_id, source_cate_name))
                            article_id = cursor2.lastrowid
                            cursor2.execute(ArticleMapper.insert_article_annex_sql_sync_latest_articles(),
                                            (content, desc, pic_url, article_id))
                            conn2.commit()
                        else:
                            log_debug("该文章已存在====================%s" % source_id)
                            pub_time = d.get("pubdate", "")
                            cursor2.execute(ArticleMapper.update_article_post_time_sql(), (pub_time, source_id))
                return True
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()
        conn2.close()


def sync_one_article(site_name, sids):
    log_debug("开始同步文章，ids： %s" % sids)
    try:
        db_conf = get_cms_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        db_conf2 = get_cms_x_db_conf(site_name)
        conn2 = pymysql.connect(**db_conf2)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            with conn2.cursor() as cursor2:
                conn2.begin()
                for sid in sids:
                    cursor.execute(ArticleMapper.select_wp_article_by_id(), (sid,))
                    d = cursor.fetchone()
                    source_id = d.get("id", None)
                    source_cate_name = d.get("cate_name", "")
                    title = d.get("title", "")
                    content = d.get("content", "")
                    content = re.sub(r'\[caption(.*)"\]', "", content)
                    content = re.sub(r'\[\/caption\]', "", content)
                    soup = BeautifulSoup(content, 'html.parser')
                    desc = soup.get_text()[0:400].replace("\n", "").replace("\r", "")
                    cursor.execute(ArticleMapper.select_wp_article_annex_by_sid(), (source_id,))
                    pic_urls = cursor.fetchall()
                    pic_url = "" if pic_urls is None or len(pic_urls) < 1 else pic_urls[0].get("pic_url", "")
                    cursor2.execute(ArticleMapper.update_article_sql(), (title, source_cate_name, sid))
                    cursor2.execute(ArticleMapper.select_article_by_source_id(), (sid,))
                    d = cursor2.fetchone()
                    article_id = d.get("id", None)
                    cursor2.execute(ArticleMapper.update_article_annex_sql(), (content, desc, pic_url, article_id))
                    conn2.commit()
                return True
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()
        conn2.close()


def del_article_item(site_name, sids):
    log_debug("开始删除文章")
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            for sid in sids:
                cursor.execute(ArticleMapper.del_article_item_sql(), (sid,))
            conn.commit()
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()
    return True


def renew_article_item(site_name, sids):
    log_debug("开始恢复文章")
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            for sid in sids:
                cursor.execute(ArticleMapper.renew_article_item_sql(), (sid,))
            conn.commit()
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()
    return True


def purge_article_item(site_name, sids):
    log_debug("开始彻底删除文章")
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            for sid in sids:
                cursor.execute(ArticleMapper.select_deleted_article_id_by_source_id(), (sid,))
                row = cursor.fetchone()
                if not row:
                    raise Exception("文章不存在或未在回收站中")
                article_id = row.get("id")
                cursor.execute(ArticleMapper.delete_article_kw_by_aid(), (article_id,))
                cursor.execute(SlugurlMapper.delete_article_slug_by_aid_sql(), (article_id,))
                cursor.execute(ArticleMapper.delete_article_ci_by_aid(), (article_id,))
                cursor.execute(ArticleMapper.delete_article_source_url_by_aid(), (article_id,))
                cursor.execute(ArticleMapper.delete_article_annex_by_aid(), (article_id,))
                cursor.execute(ArticleMapper.purge_article_by_id(), (article_id,))
            conn.commit()
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()
    return True


def get_article_list(site_name, cate_id, start_page, page_size, ai_only=False):
    log_debug("开始获取文章列表")
    try:
        cate_id = int(cate_id) if cate_id not in (None, '') else -1
    except (TypeError, ValueError):
        cate_id = -1
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(ArticleMapper.select_article_list(cate_id, ai_only), (start_page, page_size))
            datas = cursor.fetchall()
            cursor.execute(ArticleMapper.select_article_total_count(cate_id, ai_only))
            total_count = cursor.fetchone().get("num", 0)
            log_debug("返回：%s" % str(datas))
            for d in datas:
                cursor.execute(ArticleMapper.select_article_kws(), (d.get("id", None),))
                kws_datas = cursor.fetchall()
                if kws_datas is not None and len(kws_datas) > 0:
                    kws_str = ",".join(i.get("kw", "") for i in kws_datas)
                    d["kws"] = kws_str

                # 如果有父分类，同时返回父分类名称和id
                p_cate_id = d.get("p_cate_id")
                if p_cate_id:
                    cursor.execute(ArticleMapper.select_cate_by_id_sql(), (p_cate_id,))
                    parent_cate = cursor.fetchone()
                    if parent_cate:
                        d["p_cate_id"] = parent_cate.get("id")
                        d["p_cate_name"] = parent_cate.get("name")
                        d["p_cate_name_en"] = parent_cate.get("name_en")
            return datas, total_count
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_site_conf(domain):
    log_debug("开始获取站点参数配置")
    try:
        db_conf = get_cms_x_db_conf(domain)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(ArticleMapper.select_site_conf(), (domain,))
            data = cursor.fetchone()
            log_debug("返回：%s" % str(data))
            return data
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def upload_site_logo_pic(file, ext_name):
    log_debug("开始上传文件")
    try:
        t = int(arrow.now().timestamp())
        pic_name = str(t) + "_" + str(random.random()).replace(".", "")[0:8]
        path = 'upload/img/siteconf/%s.%s' % (str(pic_name), str(ext_name))
        default_storage.save(path, ContentFile(file.read()))
        log_debug("path===%s" % path)
        return path
    except Exception as e:
        raise Exception("上传图片操作失败：%s" % str(e))


def upload_defaul_pic(file, ext_name):
    log_debug("开始上传文件")
    try:
        t = int(arrow.now().timestamp())
        pic_name = str(t) + "_" + str(random.random()).replace(".", "")[0:8]
        path = 'upload/img/defaultpic/%s.%s' % (str(pic_name), str(ext_name))
        default_storage.save(path, ContentFile(file.read()))
        log_debug("path===%s" % path)
        return path
    except Exception as e:
        raise Exception("上传图片操作失败：%s" % str(e))


def update_site_conf(domain, req):
    log_debug("开始设置站点参数配置")
    try:
        db_conf = get_cms_x_db_conf(domain)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            title = req.get("title", "")
            kws = req.get("kws", "")
            desc = req.get("desc", "")
            logo_url = req.get("logo_url", "")
            defaul_pic_url = req.get("defaul_pic_url", "")
            favicon_url = req.get("favicon_url", "")
            theme_dir = req.get("theme_dir", "")
            tongji_code = req.get("tongji_code", "")
            baidu_tsapi = req.get("baidu_tsapi", "")
            https = req.get("https", "Y")
            icp = req.get("icp", "")
            site_name = req.get("site_name", "")
            conn.begin()
            cursor.execute(ArticleMapper.del_site_conf(), (domain,))
            cursor.execute(ArticleMapper.insert_site_conf(),
                           (site_name, title, logo_url, defaul_pic_url, favicon_url, icp, kws, theme_dir, tongji_code,
                            baidu_tsapi, https, desc, domain))
            conn.commit()
            return True
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


# 判断相似度的方法，用到了difflib库
def get_equal_rate(str1, str2):
    return difflib.SequenceMatcher(None, str1, str2).quick_ratio()


def match_kw_kws(site_name):
    log_debug("关键开始匹关键词")
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(ArticleMapper.select_kw_total_count())
            data = cursor.fetchone()
            total_count = 0 if data is None else data.get("num", 0)
            log_debug("total_count:::%s" % total_count)
            page_size = 10
            times = int(total_count / page_size) + 1
            log_debug("times++++++++++++%s" % times)
            # jieba.enable_paddle()  # 结巴分词配置
            for i in range(times):
                page_start = i * page_size
                cursor.execute(ArticleMapper.select_kw_list(), (page_start, page_size))
                datas = cursor.fetchall()
                for d in datas:
                    ci_list, all_related_kws, all_related_sort_kws = [], [], []
                    s_kw = d.get("kw", "")
                    s_kw_id = d.get("id", "")
                    for ci, weight in extract_tags(s_kw, topK=10, withWeight=True):
                        log_debug('%s %s' % (ci, weight))
                        ci_list.append(ci)
                    for ci in ci_list:
                        cursor.execute(ArticleMapper.select_kw_by_ci(), ('%' + ci + '%',))
                        datas2 = cursor.fetchall()
                        all_related_kws.extend(datas2)
                    ci_list_str = ("").join(ci for ci in ci_list)
                    log_debug("ci_list_str:::%s" % ci_list_str)
                    all_related_kws_tmp = []
                    for d2 in all_related_kws:
                        if d2 not in all_related_kws_tmp:
                            all_related_kws_tmp.append(d2)
                    for d3 in all_related_kws_tmp:
                        weight = get_equal_rate(d3.get("kw", ""), ci_list_str)  # 比较匹配度
                        log_debug("weight:::%s" % weight)
                        id = d3.get("id", "")
                        kw = d3.get("kw", "")
                        if kw != s_kw:
                            all_related_sort_kws.append({"id": id, "kw": kw, "weight": weight})
                    __all_related_sort_kws = sorted(all_related_sort_kws,
                                                    key=lambda s_kw: s_kw.get("weight", 0),
                                                    reverse=True)
                    cursor.execute(ArticleMapper.del_kw_kw_by_skw_id(), (s_kw_id,))
                    conn.commit()
                    kw_datas = __all_related_sort_kws[0:10]
                    count = 0
                    for kd in kw_datas:
                        count = count + 1
                        r_kw = kd.get("kw", "")
                        r_kw_id = kd.get("id", "")
                        cursor.execute(ArticleMapper.insert_kw_kw(), (s_kw_id, s_kw, r_kw_id, r_kw, count))  # 插入新kw
                    conn.commit()
            return True
    except Exception as e:
        log_error("操作数据库失败：%s" % str(e))
        raise Exception(e)
    finally:
        conn.close()


def match_some_kw_kws(site_name, ids):
    log_debug("关键词开始匹配关键词")
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            # jieba.enable_paddle()  # 结巴分词配置
            for id in ids:
                ci_list, all_related_kws, all_related_sort_kws = [], [], []
                cursor.execute(ArticleMapper.select_kw_by_id(), (id, ))
                d = cursor.fetchone()
                s_kw = d.get("kw", "")
                s_kw_id = d.get("id", "")
                for ci, weight in extract_tags(s_kw, topK=10, withWeight=True):
                    log_debug('%s %s' % (ci, weight))
                    ci_list.append(ci)
                for ci in ci_list:
                    cursor.execute(ArticleMapper.select_kw_by_ci(), ('%' + ci + '%',))
                    datas2 = cursor.fetchall()
                    all_related_kws.extend(datas2)
                ci_list_str = ("").join(ci for ci in ci_list)
                log_debug("ci_list_str:::%s" % ci_list_str)
                all_related_kws_tmp = []
                for d2 in all_related_kws:
                    if d2 not in all_related_kws_tmp:
                        all_related_kws_tmp.append(d2)
                for d3 in all_related_kws_tmp:
                    weight = get_equal_rate(d3.get("kw", ""), ci_list_str)  # 比较匹配度
                    log_debug("weight:::%s" % weight)
                    id = d3.get("id", "")
                    kw = d3.get("kw", "")
                    if kw != s_kw:
                        all_related_sort_kws.append({"id": id, "kw": kw, "weight": weight})
                __all_related_sort_kws = sorted(all_related_sort_kws,
                                                key=lambda s_kw: s_kw.get("weight", 0),
                                                reverse=True)
                cursor.execute(ArticleMapper.del_kw_kw_by_skw_id(), (s_kw_id,))
                conn.commit()
                kw_datas = __all_related_sort_kws[0:10]
                count = 0
                for kd in kw_datas:
                    count = count + 1
                    r_kw = kd.get("kw", "")
                    r_kw_id = kd.get("id", "")
                    cursor.execute(ArticleMapper.insert_kw_kw(), (s_kw_id, s_kw, r_kw_id, r_kw, count))  # 插入新kw
                conn.commit()
        return True
    except Exception as e:
        log_error("操作数据库失败：%s" % str(e))
        raise Exception(e)
    finally:
        conn.close()


def match_article_kws(site_name, flag):
    log_debug("开始一键匹配文章关键词")
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            if flag == "all":  # 全部匹配
                cursor.execute(ArticleMapper.select_article_total_count_for_match_kws())
                data = cursor.fetchone()
                total_count = 0 if data is None else data.get("num", 0)
                log_debug("total_count:::%s" % total_count)
                page_size = 20
                times = int(total_count / page_size) + 1
                log_debug("times++++++++++++%s" % times)
                for i in range(times):
                    page_start = i * page_size
                    cursor.execute(ArticleMapper.select_article_list_with_content(), (page_start, page_size))
                    datas = cursor.fetchall()
                    if datas is not None and len(datas) > 0:
                        for d in datas:
                            compute_article_kws(d, conn, cursor)
                log_debug("=====================匹配关键词完毕===============")
            else:  # 只匹配没有匹配的文章
                cursor.execute(ArticleMapper.select_article_ids_not_match_kws())
                datas = cursor.fetchall() or []
                if datas:
                    for data in datas:
                        article_id = data.get("id", None)
                        cursor.execute(ArticleMapper.select_article_by_id(), (article_id,))
                        d = cursor.fetchone()
                        compute_article_kws(d, conn, cursor)
                log_debug("=====================匹配文章关键词完毕，共计%s篇===============" % len(datas))
            return True
    except Exception as e:
        log_error("操作数据库失败：%s" % str(e))
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def compute_article_kws(d, conn, cursor):
    if not d:
        return
    article_id = d.get("id", None)
    if not article_id:
        return
    title = d.get("title") or ""
    content = d.get("content") or ""
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()

    cis, ci_list = "", []
    title_cis, title_kws, all_title_sort_kws, __all_title_sort_kws = [], [], [], []
    for ci, weight in extract_tags(title, topK=20, withWeight=True):
        log_debug('%s %s' % (ci, weight))
        title_cis.append(ci)
    title_cis_tmep = sorted(title_cis, key=lambda ci: len(ci), reverse=True)
    title_cis = title_cis_tmep[0:10]
    for ci in title_cis:
        cursor.execute(ArticleMapper.select_kw_by_ci(), ('%' + ci + '%',))
        datas2 = cursor.fetchall()
        kws = [d.get("kw", "") for d in datas2]
        title_kws.extend(list(set(kws)))
    for title_kw in set(title_kws):
        weight = get_equal_rate(title_kw, title)  # 比较匹配度
        all_title_sort_kws.append({"kw": title_kw, "weight": weight})
    __all_title_sort_kws = sorted(all_title_sort_kws, key=lambda s_kw: s_kw.get("weight", 0), reverse=True)
    title_kw_datas = __all_title_sort_kws[0:3]

    for ci, weight in extract_tags(text, topK=30, withWeight=True):
        log_debug('%s %s' % (ci, weight))
        ci_list.append(ci)
    all_related_kws, all_related_sort_kws = [], []
    ci_list_str = ("").join(ci for ci in ci_list)
    log_debug('ci_list_str：：：+++++++++ %s +++++++++' % (ci_list_str,))
    for ci in ci_list:
        cursor.execute(ArticleMapper.select_kw_by_ci(), ('%' + ci + '%',))
        datas2 = cursor.fetchall()
        if datas2 is not None and len(datas2) > 0:
            kws = [d.get("kw", "") for d in datas2]
            all_related_kws.extend(list(set(kws)))
    for kw in set(all_related_kws):
        weight = get_equal_rate(kw, ci_list_str)  # 比较匹配度
        all_related_sort_kws.append({"kw": kw, "weight": weight})
    __all_related_sort_kws = sorted(all_related_sort_kws, key=lambda s_kw: s_kw.get("weight", 0), reverse=True)
    kw_datas = __all_related_sort_kws[0:30]
    cursor.execute(ArticleMapper.del_article_kw_by_aid(), (article_id,))  # 删除已关联kw
    count, added_kws = 0, []
    for kd in title_kw_datas:
        __kw = kd.get("kw", "")
        count = count + 1
        added_kws.append(__kw)
        cursor.execute(ArticleMapper.insert_article_kw(), (article_id, __kw, count, "t"))  # 插入新kw，来自标题

    for kd in kw_datas:
        __kw = kd.get("kw", "")
        if text.find(__kw) > -1 and __kw not in added_kws and count < 10:
            count = count + 1
            added_kws.append(__kw)
            cursor.execute(ArticleMapper.insert_article_kw(), (article_id, __kw, count, "c"))  # 插入新kw，来自内容
        else:
            log_debug("文章中没有找到关键词：%s" % __kw)
    if count < 10:
        kw_datas_not_in_added_kws = [i for i in kw_datas if i.get("kw", "") not in added_kws]
        kw_datas = kw_datas_not_in_added_kws[0: 10 - count]
        for kd in kw_datas:
            count = count + 1
            __kw = kd.get("kw", "")
            cursor.execute(ArticleMapper.insert_article_kw(), (article_id, __kw, count, "r"))  # 插入新kw
    cursor.execute(ArticleMapper.update_match_kw_status(), (article_id, ))  # 更新文章匹配关键词状态
    conn.commit()
    log_debug("id为：%s的文章匹配关键词完成" % article_id)


def match_some_article_kws(site_name, sids):
    log_debug("开始匹配指定文章关键词")
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            for sid in sids:
                cursor.execute(ArticleMapper.select_article_by_sid(), (sid, ))
                data = cursor.fetchone()
                article_id = data.get("id", "")
                title = data.get("title", "")
                content = data.get("content", "")
                log_debug("article_id::: %s" % article_id)
                soup = BeautifulSoup(content, 'html.parser')
                text = soup.get_text()
                cis, ci_list = "", []
                title_cis, title_kws, all_title_sort_kws, __all_title_sort_kws = [], [], [], []
                for ci, weight in extract_tags(title, topK=20, withWeight=True):
                    log_debug('%s %s' % (ci, weight))
                    title_cis.append(ci)
                title_cis_tmep = sorted(title_cis, key=lambda ci: len(ci), reverse=True)
                title_cis = title_cis_tmep[0:10]
                for ci in title_cis:
                    cursor.execute(ArticleMapper.select_kw_by_ci(), ('%' + ci + '%',))
                    datas2 = cursor.fetchall()
                    kws = [d.get("kw", "") for d in datas2]
                    title_kws.extend(list(set(kws)))
                for title_kw in set(title_kws):
                    weight = get_equal_rate(title_kw, title)  # 比较匹配度
                    all_title_sort_kws.append({"kw": title_kw, "weight": weight})
                __all_title_sort_kws = sorted(all_title_sort_kws,
                                              key=lambda s_kw: s_kw.get("weight", 0),
                                              reverse=True)
                title_kw_datas = __all_title_sort_kws[0:3]

                for ci, weight in extract_tags(text, topK=30, withWeight=True):
                    log_debug('%s %s' % (ci, weight))
                    ci_list.append(ci)
                all_related_kws, all_related_sort_kws = [], []
                ci_list_str = ("").join(ci for ci in ci_list)
                log_debug('ci_list_str：：：+++++++++ %s +++++++++' % (ci_list_str,))
                for ci in ci_list:
                    cursor.execute(ArticleMapper.select_kw_by_ci(), ('%' + ci + '%',))
                    datas2 = cursor.fetchall()
                    kws = [d.get("kw", "") for d in datas2]
                    all_related_kws.extend(list(set(kws)))
                for kw in set(all_related_kws):
                    weight = get_equal_rate(kw, ci_list_str)  # 比较匹配度
                    all_related_sort_kws.append({"kw": kw, "weight": weight})
                __all_related_sort_kws = sorted(all_related_sort_kws,
                                                key=lambda s_kw: s_kw.get("weight", 0),
                                                reverse=True)
                kw_datas = __all_related_sort_kws[0:30]
                cursor.execute(ArticleMapper.del_article_kw_by_aid(), (article_id,))  # 删除已关联kw
                count, added_kws = 0, []
                for kd in title_kw_datas:
                    __kw = kd.get("kw", "")
                    count = count + 1
                    added_kws.append(__kw)
                    cursor.execute(ArticleMapper.insert_article_kw(), (article_id, __kw, count, "t"))  # 插入新kw，来自标题

                for kd in kw_datas:
                    __kw = kd.get("kw", "")
                    if text.find(__kw) > -1 and __kw not in added_kws and count < 10:
                        count = count + 1
                        added_kws.append(__kw)
                        cursor.execute(ArticleMapper.insert_article_kw(), (article_id, __kw, count, "c"))  # 插入新kw，来自内容
                    else:
                        log_debug("文章中没有找到关键词：%s" % __kw)
                if count < 10:
                    kw_datas_not_in_added_kws = [i for i in kw_datas if i.get("kw", "") not in added_kws]
                    kw_datas = kw_datas_not_in_added_kws[0: 10 - count]
                    for kd in kw_datas:
                        count = count + 1
                        __kw = kd.get("kw", "")
                        cursor.execute(ArticleMapper.insert_article_kw(), (article_id, __kw, count, "r"))  # 插入新kw
                cursor.execute(ArticleMapper.update_match_kw_status(), (article_id, ))  # 更新文章匹配关键词状态
                conn.commit()
            return True
    except Exception as e:
        log_error("操作数据库失败：%s" % str(e))
        raise Exception(e)
    finally:
        conn.close()


def update_article_cate(site_name, cate_id, aids):
    log_debug("开始更新文章分类")
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            for aid in aids:
                cursor.execute(ArticleMapper.update_article_cate(), (cate_id, aid))
                conn.commit()
            return True
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def update_article_defualt_cate(site_name, cate_id):
    log_debug("开始更新文章默认分类")
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(ArticleMapper.update_article_defualt_cate(), (cate_id,))
            conn.commit()
    except Exception as e:
        raise Exception("更新文章默认分类操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def update_article_pre_pub(domain, pre_pub_time, aids):
    log_debug("开始设置文章发布时间")
    try:
        db_conf = get_cms_x_db_conf(domain)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(ArticleMapper.select_site_conf(), (domain,))
            data = cursor.fetchone()
            https = data.get("https", "")
            baidu_tsapi = data.get("baidu_tsapi", "")
            prefix = "https://" if https == "Y" else "http://"
            for aid in aids:
                cursor.execute(ArticleMapper.update_article_pre_pub(), (pre_pub_time, aid))
                conn.commit()
                if baidu_tsapi != "":
                    url, ts_type, msg, success = "", "baidu", "", 1
                    cursor.execute(ArticleMapper.select_article_info_by_id(), (aid,))
                    article_info = cursor.fetchone()
                    cate_name_en = article_info.get("name_en", "")
                    s_id = article_info.get("source_id", "")
                    cursor.execute(ArticleMapper.select_ts_ret_by_sid(), (s_id, ts_type))
                    ts_ret_data = cursor.fetchone()
                    if ts_ret_data is not None and ts_ret_data.get("num") > 0:
                        log_debug("该文章链接已提交过")
                    else:
                        url = prefix + domain
                        if cate_name_en is not None and cate_name_en != "":
                            url = url + "/" + cate_name_en
                        url = url + "/" + str(s_id) + ".html"
                        headers = {'content-type': 'text/plain'}
                        data = url
                        res = requests.post(baidu_tsapi, headers=headers, data=data, timeout=10)
                        status_code = res.status_code
                        log_debug("status_code==========%s" % status_code)
                        json = res.json()
                        log_debug("json==========%s" % json)
                        if status_code == 200:
                            log_debug("推送成功")
                        else:
                            success = 0
                            msg = json.get("message", "")
                            log_debug("推送失败:::%s" % msg)
                        try:
                            cursor.execute(ArticleMapper.insert_ts_data_sql(), (url, ts_type, success, msg, s_id))
                            conn.commit()
                        except Exception as e:
                            log_debug("insert_ts_data_sql失败:::%s" % e)
                            pass
            return True
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_cate_list(site_name, start_page, page_size):
    log_debug("开始获取分类列表")
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(ArticleMapper.select_cate_list(), (start_page, page_size))
            datas = cursor.fetchall()
            cursor.execute(ArticleMapper.select_cate_total_count())
            total_count = cursor.fetchone().get("num", 0)
            return datas, total_count
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_article_cate_list(site_name):
    log_debug("开始获取分类列表")
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(ArticleMapper.select_article_cate_list())
            datas = cursor.fetchall()
            return datas
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def upload_cate_pic(file, ext_name):
    log_debug("开始上传文件")
    try:
        t = int(arrow.now().timestamp())
        pic_name = str(t) + "_" + str(random.random()).replace(".", "")[0:8]
        path = 'upload/img/cate/%s.%s' % (str(pic_name), str(ext_name))
        default_storage.save(path, ContentFile(file.read()))
        log_debug("path===%s" % path)
        return path
    except Exception as e:
        raise Exception("上传图片失败：%s" % str(e))


def check_cate_by_name(site_name, name_en, p_id):
    log_debug("check_cate开始查询该名称是否存在")
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(ArticleMapper.select_cate_by_name(), (name_en, p_id))
            data = cursor.fetchone()
            return data
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def add_cate(site_name, req):
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            name = req.get("name", "")
            name_en = req.get("name_en", "")
            pic_url = req.get("pic_url", "")
            visiable = req.get("visiable", "N")
            home_visiable = req.get("home_visiable", "N")
            sort_num = req.get("sort_num", 9999)
            seo_title = req.get("seo_title", "")
            kws = req.get("kws", "")
            desc = req.get("desc", "")
            p_id = req.get("p_id", None)
            cursor.execute(ArticleMapper.insert_cate(),
                           (name, name_en, pic_url, p_id, visiable, home_visiable, sort_num, seo_title, kws, desc))
            conn.commit()
            return True
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def update_cate(site_name, req):
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            id = req.get("id", "")
            name = req.get("name", "")
            name_en = req.get("name_en", "")
            pic_url = req.get("pic_url", "")
            visiable = req.get("visiable", "N")
            home_visiable = req.get("home_visiable", "N")
            sort_num = req.get("sort_num", 9999)
            seo_title = req.get("seo_title", "")
            kws = req.get("kws", "")
            desc = req.get("desc", "")
            p_id = req.get("p_id", None)
            cursor.execute(ArticleMapper.update_cate(),
                           (name, name_en, pic_url, p_id, visiable, home_visiable, sort_num, seo_title, kws, desc, id))
            conn.commit()
            return True
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def del_cate(site_name, id):
    log_debug("开始删除某个类别")
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(ArticleMapper.select_cate_article_total_count(), (id,))
            total_count = cursor.fetchone().get("num", 0)
            if total_count > 0:
                raise Exception("该类别下有文章，不可删除")
            cursor.execute(ArticleMapper.del_cate_by_id(), (id,))
            conn.commit()
            return True
    except Exception as e:
        raise Exception("操作失败：%s" % str(e))
    finally:
        conn.close()


def make_thumb_pic(site_name, aids=None):
    log_debug('开始生成文章的缩略图')
    if aids is not None and not isinstance(aids, (list, tuple)):
        if isinstance(aids, str):
            aids = [a for a in aids.split('___') if a]
        else:
            aids = list(aids)
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            if aids is None:
                cursor.execute(ArticleMapper.select_all_no_thumb_articles())
                articles = cursor.fetchall()
                aids = [item.get('article_id') for item in articles if item.get('article_id')]
            log_debug("content aids:::%s" % aids)
            for article_id in aids:
                cursor.execute(ArticleMapper.select_article_annex_by_aid(), (article_id,))
                article_annex = cursor.fetchone()
                content = article_annex.get("content", "")
                id = article_annex.get("id", "")
                pic_url = make_thumbnail(site_name, content, id)
                if pic_url and pic_url != "":
                    cursor.execute(ArticleMapper.update_article_thumbpic_by_id(), (pic_url, id))
                    conn.commit()
            return True
    except Exception as e:
        raise Exception("操作失败：%s" % str(e))
    finally:
        conn.close()


def make_thumbnail(pathname, content, id, width=300, height=200):
    content = content.replace("\n", "").replace("\b", "").replace("\r", "").replace("\t", "")
    pattern = '<img.*?src="(.*?)".*?/?>'
    res = re.search(pattern, str(content))
    try:
        img_url = res.groups()[0]
    except AttributeError:
        img_url = ""
    log_debug("img_url res:::%s" % img_url)
    try:
        if img_url != "":
            log_debug("============================>>>>")
            ######################################
            # 这里暂时写死，后续根据实际情况来调整   #
            ######################################
            # HREF1 = "https://www.xxx.com"
            # HREF2 = "http://www.xxx.com"
            # HREF3 = "//www.xxx.com"
            BASE_PATH = "%s/%s" % (MEDIA_ROOT, pathname)
            THUMB_PATH = "/wp-content/uploads/thumbs2"
            YEAR = arrow.now().year
            MONTH = arrow.now().month
            pic_ext_name = img_url.split(".")[-1]
            thumb_path = THUMB_PATH + "/" + str(YEAR) + "/" + str(MONTH)
            realy_thumb_path = BASE_PATH + thumb_path
            if os.path.exists(realy_thumb_path) is False:
                os.makedirs(realy_thumb_path)
            pic_url = thumb_path + "/" + str(id) + "_thumbnail" + "." + pic_ext_name
            save_path = BASE_PATH + pic_url
            log_debug("save_path:::%s" % save_path)
            log_debug("pic_url:::%s" % pic_url)
            # path = img_url.replace(HREF1, BASE_PATH)
            # path = path.replace(HREF2, BASE_PATH)
            # path = path.replace(HREF3, BASE_PATH)
            path = img_url.replace(BASE_PATH, "")
            path = BASE_PATH + path
            log_debug("path============================>>>>%s" % path)
            pixbuf = Image.open(path)
            pixbuf.thumbnail((width, height), Image.Resampling.LANCZOS)
            pixbuf.save(save_path, "jpeg")
            return pic_url
        else:
            log_debug("img_url res2:::%s" % img_url)
            return False
    except Exception as e:
        log_error("生成缩略图出现异常：%s" % str(e))
        return False


def hct_auto_post(site_name, cate_id, title, content, source_url):
    log_debug("开始发布文章====>>>%s,%s,%s,%s,%s" % (site_name, cate_id, title, content, source_url))
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            # 先验证cate_id是否存在
            if cate_id != -1:
                cursor.execute(ArticleMapper.select_cate_id_count_sql(), (cate_id,))
                num = cursor.fetchone().get("num", 0)
                if num == 0:
                    raise Exception("分类ID不存在，请填写正确的分类ID！")
            else:
                raise Exception("分类ID不能为空！")
            if title != "" and content != "":
                cursor.execute(ArticleMapper.select_article_by_title_sql(), (title, cate_id))
                aid = -1 if cursor.fetchone() is None else cursor.fetchone().get("id", -1)
                if int(aid) > -1:
                    log_debug("文章标题已存在，开始更新文章内容！")
                    conn.begin()
                    cursor.execute(ArticleMapper.update_hct_post_article_content_sql(), (content, aid))
                    conn.commit()
                else:
                    conn.begin()
                    cursor.execute(ArticleMapper.insert_hct_post_article_sql(), (title, cate_id))
                    article_id = cursor.lastrowid
                    log_debug("开始发布文章,article_id====>>>%s" % (article_id,))
                    # 记录采集源文章链接地址
                    cursor.execute(ArticleMapper.insert_cj_source_url_sql(), (article_id, source_url))
                    soup = BeautifulSoup(content, 'html.parser')
                    desc = soup.get_text()[0:200].replace("\n", "").replace("\r", "")
                    cursor.execute(ArticleMapper.insert_hct_post_article_content_sql(), (content, desc, article_id))
                    conn.commit()
            else:
                raise Exception("文章标题、内容不能为空！")
    except Exception as e:
        raise Exception("操作失败：%s" % str(e))
    finally:
        conn.close()
    return True


def update_article_desc(site_name):
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(ArticleMapper.select_no_desc_articles_sql())
            datas = cursor.fetchall()
            for d in datas:
                id = d.get("id", None)
                content = d.get("content", "")
                soup = BeautifulSoup(content, 'html.parser')
                desc = soup.get_text()[0:200].replace("\n", "").replace("\r", "")
                cursor.execute(ArticleMapper.update_article_desc_sql(), (desc, id))
    except Exception as e:
        raise Exception("操作失败：%s" % str(e))
    finally:
        conn.close()
    return True


def search_article(site_name, kw, start_page, page_size):
    log_debug("开始查找文章:::%s" % kw)
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            sql_str = ArticleMapper.search_article()
            cursor.execute(sql_str, (kw, start_page, page_size))
            datas = cursor.fetchall()
            cursor.execute(ArticleMapper.search_article_total_count(), (kw,))
            total_count = cursor.fetchone().get("num", 0)
            return datas, total_count
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_article_detail(site_name, aid):
    log_debug("开始查询文章详情:::%s" % aid)
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            sql_str = ArticleMapper.get_article_detail_sql()
            cursor.execute(sql_str, (aid,))
            data = cursor.fetchone()
            if data and data.get('content'):
                from apps.api.ai.utils.media_save import fix_content_media_urls
                data['content'] = fix_content_media_urls(data['content'], site_name)
            return data
    except Exception as e:
        raise Exception("get_article_detail操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_article_kws(site_name, aid):
    log_debug("开始查询文章关键词:::%s" % aid)
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            sql_str = ArticleMapper.select_article_kws()
            cursor.execute(sql_str, (aid,))
            data = cursor.fetchall()
            if data is not None and len(data) > 0:
                kws = [d.get("kw", "") for d in data]
                return kws
            else:
                return []
    except Exception as e:
        raise Exception("get_article_detail操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def _resolve_article_pk(cursor, article_id):
    if article_id is None:
        return None
    try:
        pk = int(article_id)
    except (TypeError, ValueError):
        return None
    if pk <= 0:
        return None
    cursor.execute('SELECT id FROM article WHERE id = %s LIMIT 1', (pk,))
    row = cursor.fetchone()
    if row:
        return pk
    cursor.execute('SELECT id FROM article WHERE source_id = %s LIMIT 1', (pk,))
    row = cursor.fetchone()
    return int(row['id']) if row else None


def add_or_update_article(site_name, article_id, cate_id, title, show_type, content, desc, kws, pic_url, slug_url, publish=False):
    log_debug(
        "新增或更新文章:::site_name=%s, article_id=%s, cate_id=%s, title=%s, publish=%s"
        % (site_name, article_id, cate_id, title, publish),
    )
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            article_pk = _resolve_article_pk(cursor, article_id)
            aid = article_pk
            # 如果desc为空，自动从content中提取
            if desc == "":
                soup = BeautifulSoup(content, 'html.parser')
                desc = soup.get_text()[0:200].replace("\n", "").replace("\r", "")
            if article_pk:
                # 更新article表
                update_article_sql = ArticleMapper.update_article_info_sql(publish)
                cursor.execute(update_article_sql, (title, cate_id, show_type, article_pk))
                # 更新article_annex表
                update_annex_sql = ArticleMapper.update_article_annex_sql_for_handadd()
                cursor.execute(update_annex_sql, (content, pic_url, desc, article_pk))
            else:
                # 新增操作
                insert_article_sql = ArticleMapper.insert_article_sql()
                cursor.execute(insert_article_sql, (title, cate_id, show_type))
                new_article_id = cursor.lastrowid
                aid = new_article_id
                insert_annex_sql = ArticleMapper.insert_article_annex_sql()
                cursor.execute(insert_annex_sql, (content, pic_url, desc, new_article_id))
            # 删除article_kw表数据
            delete_article_kw_sql = ArticleMapper.delete_article_kw_by_aid()
            cursor.execute(delete_article_kw_sql, (aid,))
            # 新增article_kw表数据
            insert_article_kw = ArticleMapper.insert_article_kw()
            if kws is not None and len(kws) > 0:
                for (idx, kw) in enumerate(kws):
                    cursor.execute(insert_article_kw, (aid, kw, idx + 1, "r"))
            # 新增article_slug表数据
            if slug_url is not None and slug_url != "":
                delete_article_slug_by_aid = SlugurlMapper.delete_article_slug_by_aid_sql()
                cursor.execute(delete_article_slug_by_aid, (aid,))
                insert_article_slug_url = SlugurlMapper.insert_article_slug_url_sql()
                cursor.execute(insert_article_slug_url, (aid, slug_url))
            if publish and aid:
                cursor.execute(ArticleMapper.publish_article_sql(), (aid,))
            conn.commit()
            return aid
    except Exception as e:
        conn.rollback()
        raise Exception("add_or_update_article操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def upload_file(site, file, ext_name):
    log_debug("开始上传文件")
    try:
        now = arrow.now()
        year_short = now.format('YY')
        month = now.format('MM')
        dir_name = '{}/{}'.format(year_short, month)
        t = int(now.timestamp())
        file_name = str(t) + "_" + str(random.random()).replace(".", "")[0:8]
        root_path = normalize_site_root_path(
            SITE_MAP.get(site, {}).get("root_path", ""),
            fallback_site_name=site,
        )
        if root_path == "":
            raise Exception("站点配置不存在，请先配置站点")
        path = '{}/upload/files/{}/{}.{}'.format(root_path, dir_name, file_name, ext_name)
        default_storage.save(path, ContentFile(file.read()))
        log_debug("path===%s" % path)
        # 剔除root_path部分，只返回相对路径
        if path.startswith(root_path):
            rel_path = path[len(root_path):]
            if rel_path.startswith('/'):
                rel_path = rel_path[1:]
            return rel_path
        return path.lstrip('/')
    except Exception as e:
        raise Exception("上传文件操作失败：%s" % str(e))


def update_cate_content(site_name, cate_id, content):
    log_debug("开始更新栏目内容")
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(ArticleMapper.update_cate_content_sql(), (content, cate_id))
            conn.commit()
            return True
    except Exception as e:
        raise Exception("操作数据库失败：%s" % str(e))
    finally:
        conn.close()