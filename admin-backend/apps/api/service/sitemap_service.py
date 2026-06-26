# coding: utf-8
import pymysql.cursors
from apps.api.utils.public import get_db_conf, get_cms_x_db_conf, log_debug, log_error
from apps.api.sql_mapper.sitemap_mapper import SiteMapMapper


def get_site_list():
    log_debug("开始获取站点列表")
    try:
        db_conf = get_db_conf()
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(SiteMapMapper.get_site_list_sql())
            datas = cursor.fetchall()
            return datas
    except Exception as e:
        raise Exception("get_site_list操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_site_conf(domain):
    log_debug("开始获取站点配置信息")
    try:
        db_conf = get_cms_x_db_conf(domain)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(SiteMapMapper.get_site_conf_sql(), (domain,))
            data = cursor.fetchone()
            return data
    except Exception as e:
        raise Exception("get_site_conf操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_topic_total_num(domain):
    log_debug("开始获取站点 %s topic总数" % domain)
    try:
        db_conf = get_cms_x_db_conf(domain)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(SiteMapMapper.get_topic_total_num_sql())
            data = cursor.fetchone()
            return data.get("num", 0)
    except Exception as e:
        raise Exception("get_topic_total_num操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_topic_ids(domain, start_num, per_sitemap_num):
    log_debug("开始获取站点 %s topic ids" % domain)
    try:
        db_conf = get_cms_x_db_conf(domain)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(SiteMapMapper.get_topic_ids_sql(), (start_num, per_sitemap_num))
            datas = cursor.fetchall()
            return [d.get("id") for d in datas]
    except Exception as e:
        raise Exception("get_topic_ids操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_cate_names(domain):
    log_debug("开始获取站点 %s get_cate_names" % domain)
    try:
        db_conf = get_cms_x_db_conf(domain)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(SiteMapMapper.get_cate_names_sql())
            datas = cursor.fetchall()
            return [d.get("name_en") for d in datas]
    except Exception as e:
        raise Exception("get_cate_ids操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_article_total_num(domain):
    log_debug("开始获取站点 %s article总数" % domain)
    try:
        db_conf = get_cms_x_db_conf(domain)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(SiteMapMapper.get_article_total_num_sql())
            data = cursor.fetchone()
            return data.get("num", 0)
    except Exception as e:
        raise Exception("get_article_total_num操作数据库失败：%s" % str(e))
    finally:
        conn.close()


def get_article_info_list(domain, start_num, per_sitemap_num):
    log_debug("开始获取站点 %s get_article_info_list" % domain)
    try:
        db_conf = get_cms_x_db_conf(domain)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(SiteMapMapper.get_article_info_list_sql(), (start_num, per_sitemap_num))
            datas = cursor.fetchall()
            return datas
    except Exception as e:
        raise Exception("get_article_info_list操作数据库失败：%s" % str(e))
    finally:
        conn.close()