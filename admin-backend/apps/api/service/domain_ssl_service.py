# coding: utf-8
"""站点域名与 SSL 证书：落盘、Nginx 配置生成、site_conf 联动。"""
from datetime import timezone

import pymysql

from apps.api.db.connection import xxgcms_connection
from apps.api.sql_mapper.base_mapper import BaseMapper
from apps.api.utils.nginx_config import (
    cert_files_exist,
    ensure_layout,
    read_cert_files,
    read_nginx_error_tail,
    remove_site_ssl_files,
    request_nginx_reload,
    write_cert_files,
    write_site_nginx_conf,
)
from apps.api.utils.public import log_debug
from apps.api.utils.site_db_init import _ensure_site_conf
from apps.api.utils.sql_init import default_db_conf
from apps.api.utils.schema_sync import ensure_xxgcms_schema
from apps.api.utils.ssl_cert import parse_aliases, validate_domain, validate_ssl_material


def _user_id(cursor, user_name):
    cursor.execute(BaseMapper.select_user_by_name(), (user_name,))
    row = cursor.fetchone()
    if not row:
        raise Exception('用户不存在')
    return row.get('id', -1)


def _get_site_for_user(user_name, site_id):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            user_id = _user_id(cursor, user_name)
            cursor.execute(BaseMapper.select_site_by_id_for_user(), (user_id, site_id))
            if not cursor.fetchone():
                raise Exception('无权访问该站点')
            cursor.execute(BaseMapper.select_site_by_id(), (site_id,))
            site = cursor.fetchone()
            if not site:
                raise Exception('站点不存在')
            return site


def _domains_for_site(site) -> list[str]:
    primary = validate_domain(site.get('name') or '')
    aliases = parse_aliases(site.get('domain_aliases') or '')
    domains = [primary]
    for alias in aliases:
        if alias not in domains:
            domains.append(alias)
    return domains


def _sync_site_conf_https(site: dict) -> None:
    site_name = (site.get('name') or '').strip()
    if not site_name:
        return
    db_conf = default_db_conf(
        site.get('db_x_host') or site.get('db_host') or '127.0.0.1',
        site.get('db_x_port') or site.get('db_port') or 3306,
        site.get('db_x_user') or site.get('db_user') or '',
        site.get('db_x_pwd') or site.get('db_pwd') or '',
        site.get('db_x_name') or site.get('db_name') or '',
    )
    _ensure_site_conf(db_conf, site_name)
    conn = pymysql.connect(
        host=db_conf['host'],
        port=int(db_conf['port']),
        user=db_conf['user'],
        password=db_conf['password'],
        database=db_conf['database'],
        charset='utf8mb4',
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE site_conf SET https = 'Y' WHERE domain = %s",
                (site_name,),
            )
        conn.commit()
    finally:
        conn.close()


def _update_site_ssl_meta(site_id, meta: dict) -> None:
    ensure_xxgcms_schema()
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    BaseMapper.update_site_ssl_meta(),
                    (
                        meta.get('domain_aliases'),
                        meta.get('ssl_enabled', 'N'),
                        meta.get('force_https', 'Y'),
                        meta.get('cert_status', 'none'),
                        meta.get('cert_not_after'),
                        meta.get('nginx_status', 'none'),
                        meta.get('nginx_error'),
                        site_id,
                    ),
                )
            except pymysql.err.OperationalError as exc:
                if exc.args and exc.args[0] == 1054:
                    ensure_xxgcms_schema(force=True)
                    cursor.execute(
                        BaseMapper.update_site_ssl_meta(),
                        (
                            meta.get('domain_aliases'),
                            meta.get('ssl_enabled', 'N'),
                            meta.get('force_https', 'Y'),
                            meta.get('cert_status', 'none'),
                            meta.get('cert_not_after'),
                            meta.get('nginx_status', 'none'),
                            meta.get('nginx_error'),
                            site_id,
                        ),
                    )
                else:
                    raise
            conn.commit()


def get_site_ssl(user_name, site_id):
    ensure_xxgcms_schema()
    site = _get_site_for_user(user_name, site_id)
    primary_domain = site.get('name') or ''
    has_certs = cert_files_exist(primary_domain)
    fullchain_pem = ''
    privkey_pem = ''
    if has_certs:
        fullchain_pem, privkey_pem = read_cert_files(primary_domain)
    return {
        'site_id': site.get('id'),
        'name': site.get('name'),
        'domain_aliases': site.get('domain_aliases') or '',
        'ssl_enabled': site.get('ssl_enabled') or 'N',
        'force_https': site.get('force_https') or 'Y',
        'cert_status': site.get('cert_status') or 'none',
        'cert_not_after': site.get('cert_not_after'),
        'nginx_status': site.get('nginx_status') or 'none',
        'nginx_error': site.get('nginx_error') or read_nginx_error_tail(),
        'has_cert_files': has_certs,
        'fullchain_pem': fullchain_pem,
        'privkey_pem': privkey_pem,
    }


def test_site_ssl(user_name, req):
    site = _get_site_for_user(user_name, req.get('site_id'))
    domain_aliases = req.get('domain_aliases', site.get('domain_aliases') or '')
    site = dict(site)
    site['domain_aliases'] = domain_aliases
    domains = _domains_for_site(site)

    fullchain = (req.get('fullchain_pem') or '').strip()
    privkey = (req.get('privkey_pem') or '').strip()
    if not fullchain or not privkey:
        if cert_files_exist(site.get('name') or ''):
            fullchain, privkey = read_cert_files(site.get('name') or '')
        else:
            raise ValueError('请提供证书链与私钥')

    info = validate_ssl_material(fullchain, privkey, domains)
    return {
        'valid': True,
        'domains': domains,
        'cert_not_after': info['not_after'].astimezone(timezone.utc).replace(tzinfo=None),
        'common_name': info.get('common_name') or '',
    }


def update_site_ssl(user_name, req):
    site_id = req.get('site_id')
    site = _get_site_for_user(user_name, site_id)
    primary_domain = validate_domain(site.get('name') or '')

    domain_aliases_raw = req.get('domain_aliases', site.get('domain_aliases') or '')
    aliases = parse_aliases(domain_aliases_raw)
    ssl_enabled = 'Y' if req.get('ssl_enabled') in (True, 'Y', 'y', 1, '1') else 'N'
    force_https = 'N' if req.get('force_https') in (False, 'N', 'n', 0, '0') else 'Y'

    site_for_domains = dict(site)
    site_for_domains['domain_aliases'] = domain_aliases_raw
    domains = _domains_for_site(site_for_domains)

    cert_not_after = site.get('cert_not_after')
    cert_status = 'none' if ssl_enabled != 'Y' else site.get('cert_status') or 'none'

    if ssl_enabled == 'Y':
        fullchain = (req.get('fullchain_pem') or '').strip()
        privkey = (req.get('privkey_pem') or '').strip()
        if not fullchain or not privkey:
            if cert_files_exist(primary_domain):
                fullchain, privkey = read_cert_files(primary_domain)
            else:
                raise ValueError('启用 HTTPS 时必须上传或粘贴证书链与私钥')

        info = validate_ssl_material(fullchain, privkey, domains)
        cert_not_after = info['not_after'].astimezone(timezone.utc).replace(tzinfo=None)
        cert_status = 'active'

        ensure_layout()
        write_cert_files(primary_domain, fullchain, privkey)
        write_site_nginx_conf(primary_domain, aliases, force_https == 'Y')
        request_nginx_reload()
        _sync_site_conf_https(site)

        nginx_status = 'pending'
        nginx_error = ''
    else:
        remove_site_ssl_files(primary_domain)
        request_nginx_reload()
        nginx_status = 'synced'
        nginx_error = ''
        cert_status = 'none'
        cert_not_after = None

    _update_site_ssl_meta(site_id, {
        'domain_aliases': domain_aliases_raw,
        'ssl_enabled': ssl_enabled,
        'force_https': force_https,
        'cert_status': cert_status,
        'cert_not_after': cert_not_after,
        'nginx_status': nginx_status,
        'nginx_error': nginx_error,
    })

    log_debug(f'SSL 配置已更新: site={primary_domain}, ssl_enabled={ssl_enabled}')
    return get_site_ssl(user_name, site_id)


def remove_site_ssl_for_domain(domain: str) -> None:
    domain = (domain or '').strip()
    if not domain:
        return
    remove_site_ssl_files(domain)
    request_nginx_reload()


def sync_site_ssl_from_record(site) -> bool:
    if (site.get('ssl_enabled') or 'N') != 'Y':
        return False
    primary = validate_domain(site.get('name') or '')
    if not cert_files_exist(primary):
        return False
    aliases = parse_aliases(site.get('domain_aliases') or '')
    force_https = (site.get('force_https') or 'Y') == 'Y'
    write_site_nginx_conf(primary, aliases, force_https)
    return True


def sync_all_enabled_sites() -> int:
    ensure_layout()
    count = 0
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(BaseMapper.select_ssl_enabled_sites())
            sites = cursor.fetchall()
    for site in sites:
        if sync_site_ssl_from_record(site):
            count += 1
    request_nginx_reload()
    return count
