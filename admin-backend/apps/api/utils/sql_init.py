# coding: utf-8
"""Execute bundled SQL dumps for local / test database setup."""
import os
from pathlib import Path

import pymysql
from pymysql.constants import CLIENT

PROJECT_SQL_DIR = Path(__file__).resolve().parents[3] / 'sql'


def _mysql_root_password():
    return (os.environ.get('XXGCMS_MYSQL_ROOT_PASSWORD') or '').strip()


def ensure_app_user_grants(host, port, database, app_user, root_password=None):
    """用 root 为应用账号补全目标库权限（新增站点 CMS 库常用）。"""
    root_password = (root_password if root_password is not None else _mysql_root_password()).strip()
    if not root_password or not database or not app_user:
        return

    safe_db = database.replace('`', '``')
    safe_user = app_user.replace("'", "''")
    conn = pymysql.connect(
        host=host,
        port=int(port),
        user='root',
        password=root_password,
        charset='utf8mb4',
        connect_timeout=10,
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"GRANT ALL PRIVILEGES ON `{safe_db}`.* TO '{safe_user}'@'%'")
            cursor.execute('FLUSH PRIVILEGES')
        conn.commit()
    finally:
        conn.close()


def _drain_multi_results(cursor):
    while True:
        try:
            cursor.fetchall()
        except pymysql.err.ProgrammingError:
            pass
        if not cursor.nextset():
            break


def prepare_mysql8_sql_session(cursor):
    """MySQL 8 执行历史 dump 前放宽 SESSION sql_mode，避免零日期默认值报错 1067。"""
    cursor.execute('SET @xxgcms_old_sql_mode = @@SESSION.sql_mode')
    cursor.execute("SET SESSION sql_mode = 'NO_AUTO_VALUE_ON_ZERO'")


def ensure_database(host, port, user, password, database):
    conn = pymysql.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        charset='utf8mb4',
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f'CREATE DATABASE IF NOT EXISTS `{database}` '
                'DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'
            )
        conn.commit()
    finally:
        conn.close()

    ensure_app_user_grants(host, port, database, user)


def execute_sql_file(db_conf, sql_path):
    sql_path = Path(sql_path)
    if not sql_path.is_file():
        raise FileNotFoundError(f'SQL 文件不存在: {sql_path}')

    sql = sql_path.read_text(encoding='utf-8')
    conn = pymysql.connect(
        host=db_conf['host'],
        port=int(db_conf['port']),
        user=db_conf['user'],
        password=db_conf['password'],
        database=db_conf['database'],
        charset=db_conf.get('charset', 'utf8mb4'),
        client_flag=CLIENT.MULTI_STATEMENTS,
    )
    try:
        with conn.cursor() as cursor:
            prepare_mysql8_sql_session(cursor)
            cursor.execute(sql)
            _drain_multi_results(cursor)
        conn.commit()
    finally:
        conn.close()


def default_db_conf(host, port, user, password, database):
    return {
        'host': host,
        'port': int(port),
        'user': user,
        'password': password,
        'database': database,
        'charset': 'utf8mb4',
    }
