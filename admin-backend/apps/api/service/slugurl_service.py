# coding: utf-8
import arrow
from django.utils.text import slugify

from apps.api.db.connection import cms_x_connection
from apps.api.sql_mapper.slugurl_mapper import SlugurlMapper
from apps.api.utils.public import log_debug


def generate_article_slug_url_by_title(site_name, article_title):
    log_debug('通过标题生成文章 slug url')
    slug_url = slugify(article_title, allow_unicode=True)[:70]
    if check_slug_url(site_name, slug_url):
        slug_url = slugify(f'{article_title}-{int(arrow.now().timestamp())}', allow_unicode=True)[:70]
    return {'slug_url': slug_url, 'article_title': article_title}


def check_slug_url(site_name, slug_url):
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(SlugurlMapper.select_slug_url_by_url_sql(), (slug_url,))
            return cursor.fetchone() is not None
