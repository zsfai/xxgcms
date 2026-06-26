# coding: utf-8
# 定时任务，任务具体执行时间在setting.py中的CRONJOBS配置
import datetime
import os
from apps.api.service import sitemap_service
from apps.api.utils.public import log_error


sitemap_dir = "sitemap"
per_sitemap_num = 9178


def create_sitemaps():
    try:
        CURR_DIR = os.path.dirname(os.path.abspath(__file__))
        API_DIR = os.path.dirname(CURR_DIR)
        APPS_DIR = os.path.dirname(API_DIR)
        XXGCMS_DIR = os.path.dirname(APPS_DIR)
        base_dir_path = XXGCMS_DIR + "/" + sitemap_dir + "/"

        site_list = sitemap_service.get_site_list()

        if os.path.exists(base_dir_path) is False:
            os.makedirs(base_dir_path)

        if site_list is not None and len(site_list) > 0:
            for site in site_list:
                sitemap_name_list = []
                try:
                    domain = site.get("name", "")
                    site_conf = sitemap_service.get_site_conf(domain)
                    https = site_conf.get("https", "N")
                    theme_dir = site_conf.get("theme_dir", domain)
                    https_str = ("https://" if https == "Y" else "http://")

                    save_path = base_dir_path + "/" + theme_dir + "/"

                    if os.path.exists(save_path) is False:
                        os.makedirs(save_path)

                    # 获取topic总数，分为多个列表，每个列表20000条
                    topic_total_num = sitemap_service.get_topic_total_num(domain)
                    if topic_total_num != 0:
                        times = int(topic_total_num / per_sitemap_num) + 1  # 生成sitemap个数
                        for i in range(times):
                            url_list = []
                            if i == 0:
                                url_list.append({
                                    "url": "%s%s" % (https_str, domain),
                                    "priority": 1,
                                    "changefreq": "weekly"
                                })
                                cate_names = sitemap_service.get_cate_names(domain)
                                for name in cate_names:
                                    url_list.append({
                                        "url": "%s%s/%s/" % (https_str, domain, name),
                                        "priority": 0.8,
                                        "changefreq": "weekly"
                                    })
                            # 获取topic链接
                            start_num = i * per_sitemap_num
                            topic_ids = sitemap_service.get_topic_ids(domain, start_num, per_sitemap_num)
                            for tid in topic_ids:
                                url_list.append({
                                    "url": "%s%s/%s/%s.html" % (https_str, domain, "topic", tid),
                                    "priority": 0.8,
                                    "changefreq": "weekly"
                                })
                            filename = "topic_sitemap_" + str(i + 1) + ".xml"
                            create_xml(save_path + filename, url_list)
                            # 注意：这里固定sitemap url，暂与nginx约定配置
                            sitemap_url = "%s%s/%s/%s" % (https_str, domain, sitemap_dir, filename)
                            sitemap_name_list.append(sitemap_url)

                    # 获取article总数，分为多个列表，每个列表20000条
                    article_total_num = sitemap_service.get_article_total_num(domain)
                    if article_total_num != 0:
                        times = int(article_total_num / per_sitemap_num) + 1  # 生成sitemap个数
                        for i in range(times):
                            url_list = []
                            # 获取article链接
                            start_num = i * per_sitemap_num
                            articles = sitemap_service.get_article_info_list(domain, start_num, per_sitemap_num)
                            for a in articles:
                                aid = a.get("source_id", None)
                                cate_name_en = a.get("name_en", "")
                                if aid is not None:
                                    if cate_name_en is None:
                                        url = "%s%s/%s.html" % (https_str, domain, aid)
                                    else:
                                        url = "%s%s/%s/%s.html" % (https_str, domain, cate_name_en, aid)
                                    url_list.append({
                                        "url": url,
                                        "priority": 0.8,
                                        "changefreq": "weekly"
                                    })
                            filename = "article_sitemap_" + str(i + 1) + ".xml"
                            create_xml(save_path + filename, url_list)
                            # 注意：这里固定sitemap url，暂与nginx约定配置
                            sitemap_url = "%s%s/%s/%s" % (https_str, domain, sitemap_dir, filename)
                            sitemap_name_list.append(sitemap_url)
                    if len(sitemap_name_list) > 0:
                        create_index_xml(sitemap_name_list, save_path + "sitemap.xml")
                except Exception as e:
                    print("生成sitemap出现异常：%s" % str(e))
    except Exception as e:
        print("生成sitemap出现异常：%s" % str(e))


def create_xml(filename, url_list):  # 生成sitemap所需要的xml方法
    header = '<?xml version="1.0" encoding="UTF-8"?>\n'
    header += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    with open(filename, 'w+') as f:
        f.writelines(header)
        for item in url_list:
            curr_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
            url = item.get("url", "")
            priority = item.get("priority", 0.8)
            changefreq = item.get("changefreq", "weekly")

            # 这个是生成的主体,可根据需求进行修改
            ment = "  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>%s</changefreq>\n    " \
                   "<priority>%s</priority>\n  </url>\n" % (url, curr_time, changefreq, priority)
            f.writelines(ment)

        last = "</urlset>"
        f.writelines(last)
        f.close()


def create_index_xml(sitemap_name_list, filename="sitemap.xml"):
    header = '<?xml version="1.0" encoding="UTF-8"?>\n'
    header += '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    with open(filename, 'w+') as f:
        f.writelines(header)

        for name in sitemap_name_list:
            times = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")

            # 这个是生成的主体,可根据需求进行修改
            ment = "  <sitemap>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n  </sitemap>\n" % (name, times)
            f.writelines(ment)

        last = "</sitemapindex>"
        f.writelines(last)
        f.close()


if __name__ == '__main__':
    sitemap_name_list = ["sitemap_1.xml", "sitemap_2.xml"]
    create_index_xml(sitemap_name_list, "sitemap_index.xml")
