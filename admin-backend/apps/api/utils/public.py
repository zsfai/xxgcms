# coding: utf-8
import logging
import os

import pymysql.cursors
from django.conf import settings

from apps.api.sql_mapper.base_mapper import BaseMapper
from apps.api.utils.base_conf import SITE_MAP

LOGGER = logging.getLogger('xxgcms')
ERROR_LOGGER = logging.getLogger('xxgcms.error')


def log_debug(msg):
    LOGGER.debug(msg)


def log_error(msg):
    ERROR_LOGGER.error(msg)


def _pymysql_conf(host, port, user, password, database):
    return {
        'host': host,
        'port': int(port),
        'user': user,
        'password': password,
        'database': database,
        'cursorclass': pymysql.cursors.DictCursor,
        'charset': 'utf8mb4',
    }


def get_db_conf():
    db = settings.XXGCMS_DB
    return _pymysql_conf(
        db['host'], db['port'], db['user'], db['password'], db['database'],
    )


def _site_db_conf(site_name, prefix):
    if not site_name:
        raise Exception('请先选择要管理的站点')
    conf = SITE_MAP.get(site_name)
    if not conf:
        raise Exception('未能读取到站点数据库配置信息')
    return _pymysql_conf(
        conf.get(f'{prefix}_host', '127.0.0.1'),
        conf.get(f'{prefix}_port', 3306),
        conf.get(f'{prefix}_user', ''),
        conf.get(f'{prefix}_pwd', ''),
        conf.get(f'{prefix}_name', ''),
    )


def get_cms_db_conf(site_name=''):
    ensure_site_map()
    return _site_db_conf(site_name, 'db')


def get_cms_x_db_conf(site_name=''):
    ensure_site_map()
    return _site_db_conf(site_name, 'db_x')


def get_client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def get_global_site_database_conf():
    log_debug('获取站点配置信息')
    if SITE_MAP:
        return SITE_MAP
    from apps.api.db.connection import xxgcms_connection

    try:
        with xxgcms_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(BaseMapper.select_site_list_without_user())
                for site in cursor.fetchall():
                    SITE_MAP[site.get('name', '')] = site
        return SITE_MAP
    except Exception as exc:
        log_error(f'启动时加载站点配置失败（将在登录后重试）：{exc}')
        return SITE_MAP


def ensure_site_map():
    if not SITE_MAP:
        get_global_site_database_conf()
    return SITE_MAP


def default_site_root_path(site_name: str) -> str:
    """站点媒体子目录（相对 MEDIA_ROOT），默认与站点标识相同。"""
    custom = os.environ.get('XXGCMS_SITE_ROOT_PATH', '').strip().strip('/')
    if custom:
        return custom
    return (site_name or '').strip().strip('/')


def normalize_site_root_path(root_path: str, fallback_site_name: str = '') -> str:
    """将 DB 中的 root_path 规范为 MEDIA_ROOT 下的相对路径。"""
    from django.conf import settings

    p = (root_path or '').strip().replace('\\', '/').strip('/')
    if not p:
        return default_site_root_path(fallback_site_name)

    media = settings.MEDIA_ROOT.rstrip('/').replace('\\', '/')
    if p.startswith(media + '/'):
        p = p[len(media) + 1:]
    elif p == media:
        p = ''

    if not p:
        return default_site_root_path(fallback_site_name)

    # 历史错误配置：绝对路径或 /tmp/xxgcms-test
    if p.startswith('tmp/') or 'xxgcms-test' in p or (root_path or '').strip().startswith('/'):
        return default_site_root_path(fallback_site_name)

    return p
