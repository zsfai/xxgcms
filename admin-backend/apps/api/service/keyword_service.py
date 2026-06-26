# coding: utf-8
import os

import arrow
import xlrd
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from apps.api.db.connection import cms_x_connection
from apps.api.sql_mapper.keyword_mapper import KeywordMapper
from apps.api.utils.public import log_debug, log_error


def _kw_slug(kw):
    return kw.replace(' ', '-').lower().replace('\u200b', '')


def _sync_kw_text_in_relations(cursor, kw_id, old_kw, new_kw):
    if not old_kw or old_kw == new_kw:
        return
    cursor.execute(KeywordMapper.update_kw_kw_source_text(), (new_kw, kw_id))
    cursor.execute(KeywordMapper.update_kw_kw_related_text(), (new_kw, kw_id))
    cursor.execute(KeywordMapper.update_article_kw_text(), (new_kw, old_kw))


def _cleanup_kw_relations(cursor, kw_id, kw_text):
    cursor.execute(KeywordMapper.del_kw_kw_by_skw_id(), (kw_id,))
    cursor.execute(KeywordMapper.del_kw_kw_by_rkw_id(), (kw_id,))
    if kw_text:
        cursor.execute(KeywordMapper.del_article_kw_by_kw(), (kw_text,))


def _attach_related_kws(cursor, datas):
    for item in datas:
        cursor.execute(KeywordMapper.select_kws_by_sid(), (item.get('id'),))
        related = cursor.fetchall()
        if related:
            item['r_kws'] = ','.join(sorted({row.get('related_kw', '') for row in related}))
    return datas


def upload_excel(domain, file, ext_name):
    log_debug('开始上传关键词 Excel')
    t = int(arrow.now().timestamp())
    path = os.path.join(settings.MEDIA_ROOT, f'upload/excel/{t}.{ext_name}')
    default_storage.save(path, ContentFile(file.read()))
    excel = xlrd.open_workbook(path)
    kws = excel.sheet_by_index(0).col_values(0)
    if not kws:
        raise Exception('没有获取到要导入的数据')

    add_kw_count = 0
    with cms_x_connection(domain) as conn:
        with conn.cursor() as cursor:
            for kw in kws:
                if not kw:
                    continue
                cursor.execute(KeywordMapper.select_kw_by_kw(), (kw,))
                if cursor.fetchall():
                    continue
                cursor.execute(KeywordMapper.insert_kw(), (kw, _kw_slug(kw)))
                add_kw_count += 1
            conn.commit()
    return add_kw_count


def get_kw_list(site_name, start_page, page_size):
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(KeywordMapper.select_kw_page(), (start_page, page_size))
            datas = list(cursor.fetchall())
            cursor.execute(KeywordMapper.select_kw_total_count())
            total_count = cursor.fetchone().get('num', 0)
            return _attach_related_kws(cursor, datas), total_count


def del_kw(site_name, kw_id):
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(KeywordMapper.select_kw_by_id(), (kw_id,))
            row = cursor.fetchone()
            if not row:
                raise Exception('关键词不存在')
            _cleanup_kw_relations(cursor, kw_id, row.get('kw', ''))
            cursor.execute(KeywordMapper.del_xpk_by_id(), (kw_id,))
            conn.commit()
    return True


def check_kw(site_name, kw):
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(KeywordMapper.select_kw_by_name(), (kw,))
            return cursor.fetchone().get('num', 0) >= 1


def add_kw(domain, kw):
    with cms_x_connection(domain) as conn:
        with conn.cursor() as cursor:
            cursor.execute(KeywordMapper.insert_kw(), (kw, _kw_slug(kw)))
            new_kw_id = cursor.lastrowid
            conn.commit()
            return new_kw_id


def update_kw(site_name, kw_id, kw):
    kw = (kw or '').strip()
    if not kw:
        raise Exception('请填写关键词')
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(KeywordMapper.select_kw_by_id(), (kw_id,))
            row = cursor.fetchone()
            if not row:
                raise Exception('关键词不存在')
            old_kw = row.get('kw', '')
            cursor.execute(KeywordMapper.count_kw_by_name_exclude_id(), (kw, kw_id))
            if cursor.fetchone().get('num', 0) >= 1:
                raise Exception('该关键词已存在')
            cursor.execute(KeywordMapper.update_kw(), (kw, _kw_slug(kw), kw_id))
            _sync_kw_text_in_relations(cursor, kw_id, old_kw, kw)
            conn.commit()
    return True


def search_kw(site_name, kw, start_page, page_size):
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(KeywordMapper.search_kw(), (f'%{kw}%', start_page, page_size))
            datas = list(cursor.fetchall())
            cursor.execute(KeywordMapper.select_kw_total_count_by_name(), (f'%{kw}%',))
            total_count = cursor.fetchone().get('num', 0)
            return _attach_related_kws(cursor, datas), total_count
