# coding: utf-8
"""数据库连接与站点配置加载。"""
import logging
import os

import pymysql.cursors
from django.conf import settings

from apps.utils.base_conf import SITE_MAP
from apps.pages.mapper import FArticleMapper

LOGGER = logging.getLogger('console')
ERROR_LOGGER = logging.getLogger('error')


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


def _site_db_conf(site, prefix):
    return _pymysql_conf(
        site.get(f'{prefix}_host', '127.0.0.1'),
        site.get(f'{prefix}_port', 3306),
        site.get(f'{prefix}_user', ''),
        site.get(f'{prefix}_pwd', ''),
        site.get(f'{prefix}_name', ''),
    )


def get_cms_db_conf(site_name=''):
    if not site_name:
        raise Exception('请先选择要管理的站点')
    conf = SITE_MAP.get(site_name)
    if not conf:
        raise Exception('未能读取到站点数据库配置信息')
    return _site_db_conf(conf, 'db')


def get_cms_x_db_conf(site_name=''):
    if not site_name:
        raise Exception('请先选择要管理的站点')
    conf = SITE_MAP.get(site_name)
    if not conf:
        raise Exception('未能读取到站点数据库配置信息')
    return _site_db_conf(conf, 'db_x')


def _normalize_host(host):
    return host.split(':')[0].strip().lower()


def _unique_sites():
    """SITE_MAP 含 name 大小写双键，按站点 id 去重。"""
    seen = set()
    unique = []
    for site in SITE_MAP.values():
        sid = site.get('id')
        key = ('id', sid) if sid is not None else ('name', site.get('name'))
        if key in seen:
            continue
        seen.add(key)
        unique.append(site)
    return unique


def _resolve_site(host):
    """按 HTTP_HOST 匹配站点：先精确匹配（含端口），再匹配去掉端口的主机名。"""
    if not host:
        return None
    raw = host.strip().lower()
    if raw in SITE_MAP:
        return SITE_MAP[raw]

    bare = _normalize_host(host)
    if bare != raw and bare in SITE_MAP:
        return SITE_MAP[bare]

    for site in SITE_MAP.values():
        name = (site.get('name') or '').strip().lower()
        if name and name in (raw, bare):
            return site

    # Docker / 离线单站点：IP 访问时回退到环境变量或唯一站点
    fallback = (
        os.environ.get('XXGCMS_DEFAULT_SITE')
        or os.environ.get('XXGCMS_CMS_SITE_NAME')
        or ''
    ).strip()
    if fallback:
        site = SITE_MAP.get(fallback) or SITE_MAP.get(fallback.lower())
        if site:
            return site

    unique = _unique_sites()
    if len(unique) == 1:
        return unique[0]
    return None


def resolve_site_domains(host):
    """用于 site_conf 查询：HTTP_HOST + 站点标识。"""
    domains = []
    for value in (host,):
        if value and value not in domains:
            domains.append(value)
    site = _resolve_site(host)
    if site:
        name = (site.get('name') or '').strip()
        if name and name not in domains:
            domains.append(name)
    return domains


def _register_site(site):
    name = (site.get('name') or '').strip()
    if not name:
        return
    SITE_MAP[name] = site
    SITE_MAP[name.lower()] = site


def ensure_site_map():
    """SITE_MAP 为空时从系统库重新加载（启动过早或首次连库失败时可恢复）。"""
    if SITE_MAP:
        return SITE_MAP
    return get_global_site_database_conf()


def get_cms_front_db_conf(host):
    ensure_site_map()
    site = _resolve_site(host)
    if not site:
        raise Exception(f'未找到与域名 {host} 对应的站点配置')
    return _site_db_conf(site, 'db_x')


def get_client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def get_global_site_database_conf():
    log_debug('获取站点配置信息')
    if SITE_MAP:
        return SITE_MAP
    try:
        db_conf = get_db_conf()
        conn = pymysql.connect(**db_conf)
    except Exception as exc:
        raise Exception(f'数据库链接失败:{exc}') from exc
    try:
        with conn.cursor() as cursor:
            cursor.execute(FArticleMapper.select_site_list())
            for site in cursor.fetchall():
                _register_site(site)
        return SITE_MAP
    except Exception as exc:
        raise Exception(f'操作数据库失败：{exc}') from exc
    finally:
        conn.close()


def _preload_site_map():
    try:
        get_global_site_database_conf()
    except Exception as exc:
        log_error(f'启动时加载站点配置失败（将在首次请求时重试）：{exc}')


_preload_site_map()
