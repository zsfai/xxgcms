# coding: utf-8
"""新增站点时自动创建 CMS 数据库并执行 cmsdb.sql。"""
import os

import pymysql

from apps.api.utils.public import log_debug
from apps.api.utils.mysql8_upgrade import upgrade_cms_database
from apps.api.utils.sql_init import (
    PROJECT_SQL_DIR,
    default_db_conf,
    ensure_database,
    execute_sql_file,
)

CMS_SQL_FILE = PROJECT_SQL_DIR / 'cmsdb.sql'
CMS_MARKER_TABLES = ('article', 'site_conf', 'cate', 'keyword')


def cms_db_conf_from_req(req):
    host = (req.get('db_x_host') or '').strip()
    port = int(req.get('db_x_port') or 3306)
    database = (req.get('db_x_name') or '').strip()
    user = (req.get('db_x_user') or '').strip()
    password = req.get('db_x_pwd') or ''
    if not host:
        raise Exception('请填写数据库主机')
    if not database:
        raise Exception('请填写数据库名')
    if not user:
        raise Exception('请填写数据库用户名')
    return default_db_conf(host, port, user, password, database)


def _connect_server(host, port, user, password, database=None):
    kwargs = {
        'host': host,
        'port': int(port),
        'user': user,
        'password': password,
        'charset': 'utf8mb4',
        'connect_timeout': 10,
    }
    if database:
        kwargs['database'] = database
    return pymysql.connect(**kwargs)


def test_cms_database(req):
    """测试连接；返回库是否存在、是否已有 CMS 表。"""
    conf = cms_db_conf_from_req(req)
    host, port, user, password, database = (
        conf['host'], conf['port'], conf['user'], conf['password'], conf['database'],
    )

    try:
        conn = _connect_server(host, port, user, password)
    except pymysql.err.OperationalError as exc:
        raise Exception(f'无法连接数据库服务器：{exc}') from exc
    finally:
        if 'conn' in locals():
            conn.close()

    db_exists = False
    has_cms_tables = False
    table_count = 0

    conn = _connect_server(host, port, user, password)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s',
                (database,),
            )
            db_exists = cursor.fetchone() is not None

            if db_exists:
                cursor.execute(
                    'SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s',
                    (database,),
                )
                tables = {row[0] for row in cursor.fetchall()}
                table_count = len(tables)
                has_cms_tables = any(name in tables for name in CMS_MARKER_TABLES)
    finally:
        conn.close()

    return {
        'connected': True,
        'database': database,
        'database_exists': db_exists,
        'has_cms_tables': has_cms_tables,
        'table_count': table_count,
    }


def _has_cms_core_tables(db_conf):
    conn = _connect_server(
        db_conf['host'],
        db_conf['port'],
        db_conf['user'],
        db_conf['password'],
        db_conf['database'],
    )
    try:
        with conn.cursor() as cursor:
            placeholders = ','.join(['%s'] * len(CMS_MARKER_TABLES))
            cursor.execute(
                f'SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES '
                f'WHERE TABLE_SCHEMA = %s AND TABLE_NAME IN ({placeholders})',
                (db_conf['database'], *CMS_MARKER_TABLES),
            )
            return cursor.fetchone()[0] > 0
    finally:
        conn.close()


def _ensure_site_conf(db_conf, site_name):
    domain = site_name.strip()
    if not domain:
        return

    conn = _connect_server(
        db_conf['host'],
        db_conf['port'],
        db_conf['user'],
        db_conf['password'],
        db_conf['database'],
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT domain FROM site_conf WHERE domain = %s LIMIT 1', (domain,))
            if cursor.fetchone():
                return
            cursor.execute(
                '''
                INSERT INTO site_conf (site_name, domain, theme_dir, https, add_time)
                VALUES (%s, %s, %s, %s, NOW())
                ''',
                (domain, domain, os.environ.get('XXGCMS_DEFAULT_THEME', 'www_xxg_ai'), 'Y'),
            )
        conn.commit()
    finally:
        conn.close()


def init_site_cms_database(req, site_name):
    """
    创建数据库（若不存在）并执行 cmsdb.sql。
    若目标库已有 CMS 核心表，则跳过建表，仅补全 site_conf。
    """
    if not CMS_SQL_FILE.is_file():
        raise FileNotFoundError(f'SQL 模板不存在: {CMS_SQL_FILE}')

    db_conf = cms_db_conf_from_req(req)
    host, port, user, password, database = (
        db_conf['host'], db_conf['port'], db_conf['user'],
        db_conf['password'], db_conf['database'],
    )

    log_debug(f'初始化 CMS 库 {database} @ {host}:{port}')
    ensure_database(host, port, user, password, database)

    if _has_cms_core_tables(db_conf):
        _ensure_site_conf(db_conf, site_name)
        return {
            'initialized': False,
            'message': '目标数据库已有 CMS 表结构，已跳过建表',
        }

    execute_sql_file(db_conf, CMS_SQL_FILE)
    upgrade_cms_database(db_conf)
    _ensure_site_conf(db_conf, site_name)
    return {
        'initialized': True,
        'message': 'CMS 数据库表初始化完成',
    }
