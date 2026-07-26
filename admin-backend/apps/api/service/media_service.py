# coding: utf-8
import os
import random

import arrow
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from apps.api.db.connection import cms_x_connection
from apps.api.sql_mapper.media_mapper import MediaMapper
from apps.api.utils.base_conf import SITE_MAP
from apps.api.utils.public import ensure_site_map, log_error, normalize_site_root_path
from apps.api.utils.upload import (
    MEDIA_MAX_FILE_SIZE,
    classify_file_type,
    validate_media_ext,
)


def _media_url(file_path):
    path = (file_path or '').replace('\\', '/').lstrip('/')
    if not path:
        return ''
    return '/media/%s' % path


def _decorate_row(row):
    if not row:
        return row
    item = dict(row)
    item['url'] = _media_url(item.get('file_path'))
    return item


def get_media_list(site_name, start_page, page_size, file_type=None, keyword=None):
    file_type = (file_type or '').strip() or None
    if file_type and file_type not in ('image', 'document', 'video', 'other'):
        raise ValueError('无效的文件类型')
    kw = (keyword or '').strip()
    kw_like = ('%%%s%%' % kw) if kw else None

    params = []
    if file_type:
        params.append(file_type)
    if kw_like:
        params.append(kw_like)

    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            list_params = list(params) + [start_page, page_size]
            cursor.execute(
                MediaMapper.select_media_page_list(file_type=file_type, keyword=kw_like),
                tuple(list_params),
            )
            datas = [_decorate_row(row) for row in cursor.fetchall()]
            cursor.execute(
                MediaMapper.select_media_total_count(file_type=file_type, keyword=kw_like),
                tuple(params),
            )
            total_count = cursor.fetchone().get('num', 0)
            return datas, total_count


def upload_media(site_name, uploaded_file):
    ensure_site_map()
    original_name = getattr(uploaded_file, 'name', '') or 'unnamed'
    ext = validate_media_ext(original_name.rsplit('.', 1)[-1] if '.' in original_name else '')
    file_type = classify_file_type(ext)

    file_size = getattr(uploaded_file, 'size', None)
    if file_size is None:
        content = uploaded_file.read()
        file_size = len(content)
    else:
        content = uploaded_file.read()
        file_size = int(file_size)

    if file_size > MEDIA_MAX_FILE_SIZE:
        raise ValueError('文件大小不能超过 50MB')

    root_path = normalize_site_root_path(
        SITE_MAP.get(site_name, {}).get('root_path', ''),
        fallback_site_name=site_name,
    )
    if not root_path:
        raise ValueError('站点配置不存在，请先配置站点')

    now = arrow.now()
    dir_name = '%s/%s' % (now.format('YY'), now.format('MM'))
    file_name = '%s_%s' % (int(now.timestamp()), str(random.random()).replace('.', '')[:8])
    rel_path = '%s/upload/library/%s/%s.%s' % (root_path, dir_name, file_name, ext)
    default_storage.save(rel_path, ContentFile(content))

    display_name = os.path.basename(original_name)
    if len(display_name) > 255:
        display_name = display_name[:255]

    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                MediaMapper.insert_media(),
                (display_name, rel_path, ext, file_type, file_size),
            )
            media_id = cursor.lastrowid
            conn.commit()
            cursor.execute(MediaMapper.select_media_by_id(), (media_id,))
            row = cursor.fetchone()
            return _decorate_row(row)


def rename_media(site_name, media_id, name):
    name = (name or '').strip()
    if not name:
        raise ValueError('名称不能为空')
    if len(name) > 255:
        name = name[:255]

    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(MediaMapper.select_media_by_id(), (media_id,))
            if not cursor.fetchone():
                raise ValueError('文件不存在')
            cursor.execute(MediaMapper.rename_media(), (name, media_id))
            conn.commit()
    return True


def del_media(site_name, media_id):
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(MediaMapper.select_media_by_id(), (media_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError('文件不存在')
            file_path = row.get('file_path') or ''
            cursor.execute(MediaMapper.del_media(), (media_id,))
            conn.commit()

    if file_path:
        try:
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
        except Exception as exc:
            log_error('删除媒体文件失败 %s: %s' % (file_path, str(exc)))
    return True
