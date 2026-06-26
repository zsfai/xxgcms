# coding: utf-8
import requests
import arrow
import pymysql.cursors

from apps.api.utils.public import get_cms_x_db_conf, log_debug, log_error
from apps.api.sql_mapper.xxgcms_post_mapper import XxgcmsPostMapper
from apps.api.sql_mapper.article_mapper import ArticleMapper
from apps.api.service import article_service


def post_article_service(site_name=""):
    log_debug("开始定时发布文章")
    curr_hour = arrow.now().hour
    if curr_hour < 6:
        return False
    try:
        db_conf = get_cms_x_db_conf(site_name)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        log_error("数据库链接失败：%s" % str(e))
        raise Exception("数据库链接失败:%s" % str(e))
    try:
        with conn.cursor() as cursor:
            cursor.execute(XxgcmsPostMapper.select_rand_post_article_id_sql())
            data = cursor.fetchone()
            if data is not None:
                aid = data.get("id", None)
                cursor.execute(ArticleMapper.select_article_by_id(), (aid,))
                d = cursor.fetchone()
                # 匹配关键词，暂时写在这里
                article_service.compute_article_kws(d, conn, cursor)
                cursor.execute(XxgcmsPostMapper.post_article_sql(), (aid,))
                conn.commit()
    except Exception as e:
        log_error("post_article_service：%s" % str(e))
    finally:
        conn.close()


def ts_article_service(domain=""):
    try:
        db_conf = get_cms_x_db_conf(domain)
        conn = pymysql.connect(**db_conf)
    except Exception as e:
        log_error("数据库链接失败：%s" % str(e))
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute(ArticleMapper.select_site_conf(), (domain,))
            data = cursor.fetchone()
            https = data.get("https", "")
            baidu_tsapi = data.get("baidu_tsapi", "")
            prefix = "https://" if https == "Y" else "http://"
            cursor.execute(XxgcmsPostMapper.select_no_ts_articles())
            datas = cursor.fetchall()
            aids = [d.get("id", -1) for d in datas]
            if len(aids) == 0:
                log_debug("没有文章需要推送")
                return False
            for aid in aids:
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
    except Exception as e:
        log_error("操作数据库失败：%s" % str(e))
    finally:
        conn.close()