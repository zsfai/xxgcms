# coding: utf-8
import base64
import hashlib
import os
import re

import markdown

from apps.api.ai.utils.media_save import save_ai_image, to_media_url
from apps.api.db.connection import cms_x_connection, xxgcms_connection
from apps.api.service import article_service, media_service
from apps.api.sql_mapper.base_mapper import BaseMapper
from apps.api.utils.image_normalize import normalize_image_bytes
from apps.api.utils.public import ensure_site_map, log_error

_HTML_HINT_RE = re.compile(r'<(p|div|h[1-6]|article|section|ul|ol|table|img|br)\b', re.I)


def list_sites_for_key(key_row):
    user_id = key_row.get('user_id')
    bound_site_id = key_row.get('site_id')
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(BaseMapper.select_site_list(), (user_id,))
            sites = cursor.fetchall()
    if bound_site_id:
        sites = [row for row in sites if row.get('id') == bound_site_id]
    return [
        {
            'id': row.get('id'),
            'name': row.get('name'),
            'desc': row.get('desc') or '',
        }
        for row in sites
    ]


def resolve_site_name(key_row, site_name):
    name = (site_name or '').strip()
    sites = list_sites_for_key(key_row)
    if not sites:
        raise ValueError('当前密钥没有可写入的站点')
    if not name:
        if len(sites) == 1:
            return sites[0]['name']
        raise ValueError('请指定 site（站点 name）。可用 list_sites 查看')
    for row in sites:
        if row.get('name') == name:
            return name
    raise ValueError('无权访问站点：%s' % name)


def list_categories(site_name):
    ensure_site_map()
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                SELECT id, name, name_en, visiable, home_visiable
                FROM cate
                WHERE del_flag = 'N'
                ORDER BY sort_num ASC, id ASC
                ''',
            )
            return cursor.fetchall()


def _escape_like(value):
    return value.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


def resolve_or_create_cate(site_name, category_name):
    name = (category_name or '').strip()
    if not name:
        raise ValueError('category_name 不能为空')
    if len(name) > 100:
        name = name[:100]

    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                'SELECT id, name, name_en FROM cate WHERE del_flag = %s AND name = %s LIMIT 2',
                ('N', name),
            )
            exact = cursor.fetchall()
            if len(exact) == 1:
                return exact[0]['id'], False
            if len(exact) > 1:
                return exact[0]['id'], False

            cursor.execute(
                'SELECT id, name, name_en FROM cate WHERE del_flag = %s AND LOWER(name_en) = LOWER(%s) LIMIT 2',
                ('N', name),
            )
            by_en = cursor.fetchall()
            if len(by_en) == 1:
                return by_en[0]['id'], False

            like = '%' + _escape_like(name) + '%'
            cursor.execute(
                r"SELECT id, name, name_en FROM cate WHERE del_flag = %s AND name LIKE %s ESCAPE '\\'",
                ('N', like),
            )
            fuzzy = cursor.fetchall()
            if len(fuzzy) == 1:
                return fuzzy[0]['id'], False

            name_en = 'mcp_' + hashlib.sha1(name.encode('utf-8')).hexdigest()[:10]
            base = name_en
            suffix = 1
            while True:
                cursor.execute(
                    'SELECT id FROM cate WHERE name_en = %s LIMIT 1',
                    (name_en,),
                )
                if not cursor.fetchone():
                    break
                suffix += 1
                name_en = '%s_%s' % (base, suffix)

            cursor.execute(
                '''
                INSERT INTO cate (
                    name, name_en, pic_url, p_id, visiable, home_visiable,
                    sort_num, seo_title, kws, `desc`, add_time
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ''',
                (name, name_en, '', None, 'N', 'N', 9999, '', '', ''),
            )
            cate_id = cursor.lastrowid
            conn.commit()
            return cate_id, True


def _decode_base64(value):
    raw = (value or '').strip()
    if not raw:
        raise ValueError('图片内容为空')
    if ',' in raw and raw.lower().startswith('data:'):
        raw = raw.split(',', 1)[1]
    try:
        return base64.b64decode(raw)
    except Exception as exc:
        raise ValueError('图片 base64 无效') from exc


def save_normalized_image(site_name, filename, content_base64):
    ensure_site_map()
    data = _decode_base64(content_base64)
    jpeg_bytes, ext = normalize_image_bytes(data, filename)
    stored = save_ai_image(site_name, jpeg_bytes, ext)
    display = os.path.basename(filename or '') or 'mcp-image.jpg'
    if not display.lower().endswith('.jpg') and not display.lower().endswith('.jpeg'):
        display = os.path.splitext(display)[0] + '.jpg'
    try:
        media_service.register_saved_file(site_name, display, stored, ext, len(jpeg_bytes))
    except Exception as exc:
        log_error('MCP 图片登记媒体库失败: %s' % exc)
    url = to_media_url(site_name, stored)
    return {
        'url': url,
        'path': stored,
        'bytes': len(jpeg_bytes),
        'width_limit': 1200,
    }


def _content_to_html(content):
    text = content or ''
    if _HTML_HINT_RE.search(text):
        return text
    return markdown.markdown(text, extensions=['extra', 'nl2br', 'sane_lists'])


def push_article(
    site_name,
    title,
    content,
    category_name,
    summary='',
    keywords=None,
    cover_image_base64='',
    cover_url='',
):
    ensure_site_map()
    title = (title or '').strip()
    if not title:
        raise ValueError('title 不能为空')
    if len(title) > 200:
        title = title[:200]

    cate_id, cate_created = resolve_or_create_cate(site_name, category_name)
    html = _content_to_html(content)
    pic_url = (cover_url or '').strip()
    if cover_image_base64:
        saved = save_normalized_image(site_name, 'cover.jpg', cover_image_base64)
        pic_url = saved['path']
    elif pic_url.startswith('/media/'):
        pic_url = pic_url[len('/media/'):].lstrip('/')

    kws = keywords if isinstance(keywords, list) else []
    kws = [str(item).strip() for item in kws if str(item).strip()]

    article_id = article_service.add_or_update_article(
        site_name,
        -1,
        cate_id,
        title,
        1,
        html,
        (summary or '').strip(),
        kws,
        pic_url,
        '',
        publish=False,
    )
    return {
        'article_id': article_id,
        'cate_id': cate_id,
        'cate_created': cate_created,
        'pub_status': 'N',
        'title': title,
    }
