# coding: utf-8
"""Compare bundled SQL schema with live database; add missing tables/columns."""
import re
from pathlib import Path

import pymysql

from apps.api.utils.sql_init import prepare_mysql8_sql_session

CREATE_TABLE_RE = re.compile(
    r'(CREATE TABLE `[^`]+`\s*\(.*?\)\s*ENGINE=[^;]+;)',
    re.DOTALL | re.IGNORECASE,
)
TABLE_NAME_RE = re.compile(r'CREATE TABLE `([^`]+)`', re.IGNORECASE)
TABLE_BODY_RE = re.compile(
    r'CREATE TABLE `[^`]+`\s*\((.*)\)\s*ENGINE',
    re.DOTALL | re.IGNORECASE,
)
CONSTRAINT_PREFIXES = (
    'PRIMARY KEY',
    'UNIQUE KEY',
    'KEY ',
    'CONSTRAINT',
    'FULLTEXT',
    'SPATIAL',
)


def parse_sql_schema(sql_path):
    sql_text = Path(sql_path).read_text(encoding='utf-8')
    tables = {}
    for match in CREATE_TABLE_RE.finditer(sql_text):
        create_sql = match.group(1)
        table_name = TABLE_NAME_RE.search(create_sql).group(1)
        body = TABLE_BODY_RE.search(create_sql).group(1)
        columns = {}
        for line in body.split('\n'):
            line = line.strip().rstrip(',')
            if not line.startswith('`'):
                continue
            upper = line.upper()
            if any(upper.startswith(prefix) for prefix in CONSTRAINT_PREFIXES):
                continue
            col_match = re.match(r'`([^`]+)`\s+(.+)', line, re.IGNORECASE)
            if col_match:
                columns[col_match.group(1)] = col_match.group(2)
        tables[table_name] = {
            'create_sql': create_sql,
            'columns': columns,
        }
    return tables


def _fetch_names(cursor, sql, params):
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    names = set()
    for row in rows:
        if isinstance(row, dict):
            names.add(next(iter(row.values())))
        else:
            names.add(row[0])
    return names


def _existing_tables(cursor, database):
    return _fetch_names(
        cursor,
        'SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s',
        (database,),
    )


def _existing_columns(cursor, database, table):
    return _fetch_names(
        cursor,
        'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS '
        'WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s',
        (database, table),
    )


def sync_schema(db_conf, sql_path, dry_run=False):
    expected = parse_sql_schema(sql_path)
    database = db_conf['database']
    changes = []

    conn = pymysql.connect(
        host=db_conf['host'],
        port=int(db_conf['port']),
        user=db_conf['user'],
        password=db_conf['password'],
        database=database,
        charset=db_conf.get('charset', 'utf8mb4'),
    )
    try:
        with conn.cursor() as cursor:
            if not dry_run:
                prepare_mysql8_sql_session(cursor)
            existing_tables = _existing_tables(cursor, database)
            for table, spec in expected.items():
                if table not in existing_tables:
                    changes.append({
                        'action': 'CREATE TABLE',
                        'table': table,
                        'sql': spec['create_sql'],
                    })
                    if not dry_run:
                        cursor.execute(spec['create_sql'])
                    continue

                existing_columns = _existing_columns(cursor, database, table)
                for column, definition in spec['columns'].items():
                    if column in existing_columns:
                        continue
                    alter_sql = (
                        f'ALTER TABLE `{table}` ADD COLUMN `{column}` {definition}'
                    )
                    changes.append({
                        'action': 'ADD COLUMN',
                        'table': table,
                        'column': column,
                        'sql': alter_sql,
                    })
                    if not dry_run:
                        cursor.execute(alter_sql)

        if not dry_run:
            conn.commit()
    finally:
        conn.close()

    return changes


_XXGCMS_SCHEMA_SYNCED = False


def ensure_xxgcms_schema(force=False):
    """已有部署升级时补齐 xxgcms.sql 中缺失的表/字段（进程内只执行一次）。"""
    global _XXGCMS_SCHEMA_SYNCED
    if _XXGCMS_SCHEMA_SYNCED and not force:
        return []

    from django.conf import settings

    from apps.api.utils.sql_init import PROJECT_SQL_DIR, default_db_conf

    db = settings.XXGCMS_DB
    db_conf = default_db_conf(
        db['host'],
        db['port'],
        db['user'],
        db['password'],
        db['database'],
    )
    changes = sync_schema(db_conf, PROJECT_SQL_DIR / 'xxgcms.sql', dry_run=False)
    _XXGCMS_SCHEMA_SYNCED = True
    return changes
