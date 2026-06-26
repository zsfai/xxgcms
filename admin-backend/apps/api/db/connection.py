# coding: utf-8
"""PyMySQL connection helpers."""
from contextlib import contextmanager

import pymysql


@contextmanager
def db_connection(db_conf):
    conn = pymysql.connect(**db_conf)
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def xxgcms_connection():
    from apps.api.utils.public import get_db_conf
    with db_connection(get_db_conf()) as conn:
        yield conn


@contextmanager
def cms_connection(site_name):
    from apps.api.utils.public import get_cms_db_conf
    with db_connection(get_cms_db_conf(site_name)) as conn:
        yield conn


@contextmanager
def cms_x_connection(site_name):
    from apps.api.utils.public import get_cms_x_db_conf
    with db_connection(get_cms_x_db_conf(site_name)) as conn:
        yield conn


@contextmanager
def cursor_from(conf):
    with db_connection(conf) as conn:
        with conn.cursor() as cursor:
            yield conn, cursor
