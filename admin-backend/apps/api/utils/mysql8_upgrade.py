# coding: utf-8
"""将 MySQL 5.7 遗留结构升级为 MySQL 8.0 兼容（零日期、字符集等）。"""
from pymysql.constants import CLIENT

from apps.api.utils.sql_init import execute_sql_file, PROJECT_SQL_DIR

MYSQL8_COLLATION = 'utf8mb4_unicode_ci'

# CMS 库中需修复的 datetime 列（5.7 零日期在 8.0 严格模式下不可用）
CMS_DATETIME_COLUMNS = (
    {
        'table': 'article',
        'column': 'add_time',
        'not_null': True,
        'default': 'CURRENT_TIMESTAMP',
        'zero_fallback': '1970-01-01 00:00:00',
    },
    {
        'table': 'article_kw',
        'column': 'add_time',
        'not_null': True,
        'default': 'CURRENT_TIMESTAMP',
        'zero_fallback': '1970-01-01 00:00:00',
    },
    {
        'table': 'cate',
        'column': 'add_time',
        'not_null': False,
        'default': None,
        'zero_fallback': None,
    },
)


def _table_exists(cursor, database, table):
    cursor.execute(
        'SELECT 1 FROM INFORMATION_SCHEMA.TABLES '
        'WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s LIMIT 1',
        (database, table),
    )
    return cursor.fetchone() is not None


def _column_exists(cursor, database, table, column):
    cursor.execute(
        'SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS '
        'WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s LIMIT 1',
        (database, table, column),
    )
    return cursor.fetchone() is not None


def _relax_zero_date_mode(cursor):
    cursor.execute('SET @xxgcms_old_sql_mode = @@SESSION.sql_mode')
    cursor.execute(
        "SET SESSION sql_mode = REPLACE(REPLACE(@@SESSION.sql_mode, "
        "'NO_ZERO_DATE', ''), 'NO_ZERO_IN_DATE', '')"
    )


def _restore_sql_mode(cursor):
    cursor.execute('SET SESSION sql_mode = @xxgcms_old_sql_mode')


def _alter_database_charset(cursor, database):
    cursor.execute(
        f'ALTER DATABASE `{database}` CHARACTER SET utf8mb4 COLLATE {MYSQL8_COLLATION}'
    )


def _fix_cms_datetime_columns(cursor, database, dry_run=False):
    changes = []
    _relax_zero_date_mode(cursor)
    try:
        for spec in CMS_DATETIME_COLUMNS:
            table = spec['table']
            column = spec['column']
            if not _table_exists(cursor, database, table):
                continue
            if not _column_exists(cursor, database, table, column):
                continue

            if spec['zero_fallback'] is not None:
                update_sql = (
                    f"UPDATE `{table}` SET `{column}` = %s "
                    f"WHERE `{column}` = '0000-00-00 00:00:00' OR `{column}` IS NULL"
                )
                changes.append({
                    'action': 'FIX ZERO DATE',
                    'table': table,
                    'column': column,
                    'sql': update_sql,
                    'params': (spec['zero_fallback'],),
                })
                if not dry_run:
                    cursor.execute(update_sql, (spec['zero_fallback'],))
            elif not spec['not_null']:
                update_sql = (
                    f"UPDATE `{table}` SET `{column}` = NULL "
                    f"WHERE `{column}` = '0000-00-00 00:00:00'"
                )
                changes.append({
                    'action': 'FIX ZERO DATE',
                    'table': table,
                    'column': column,
                    'sql': update_sql,
                })
                if not dry_run:
                    cursor.execute(update_sql)

            null_sql = 'NOT NULL' if spec['not_null'] else 'NULL'
            if spec['default'] == 'CURRENT_TIMESTAMP':
                default_sql = 'DEFAULT CURRENT_TIMESTAMP'
            elif spec['default'] is None:
                default_sql = 'DEFAULT NULL'
            else:
                default_sql = f"DEFAULT '{spec['default']}'"
            alter_sql = (
                f'ALTER TABLE `{table}` MODIFY COLUMN `{column}` '
                f'datetime {null_sql} {default_sql}'
            )
            changes.append({
                'action': 'ALTER COLUMN',
                'table': table,
                'column': column,
                'sql': alter_sql,
            })
            if not dry_run:
                cursor.execute(alter_sql)
    finally:
        _restore_sql_mode(cursor)
    return changes


def upgrade_cms_database(db_conf, dry_run=False, convert_tables=False):
    """升级单个 CMS 站点库。"""
    import pymysql

    database = db_conf['database']
    changes = []

    conn = pymysql.connect(
        host=db_conf['host'],
        port=int(db_conf['port']),
        user=db_conf['user'],
        password=db_conf['password'],
        database=database,
        charset=db_conf.get('charset', 'utf8mb4'),
        client_flag=CLIENT.MULTI_STATEMENTS,
    )
    try:
        with conn.cursor() as cursor:
            alter_db_sql = (
                f'ALTER DATABASE `{database}` CHARACTER SET utf8mb4 '
                f'COLLATE {MYSQL8_COLLATION}'
            )
            changes.append({
                'action': 'ALTER DATABASE',
                'database': database,
                'sql': alter_db_sql,
            })
            if not dry_run:
                _alter_database_charset(cursor, database)

            changes.extend(_fix_cms_datetime_columns(cursor, database, dry_run=dry_run))

            if convert_tables and not dry_run:
                cursor.execute(
                    'SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES '
                    'WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = %s',
                    (database, 'BASE TABLE'),
                )
                for (table_name,) in cursor.fetchall():
                    alter_table_sql = (
                        f'ALTER TABLE `{table_name}` '
                        f'CONVERT TO CHARACTER SET utf8mb4 COLLATE {MYSQL8_COLLATION}'
                    )
                    changes.append({
                        'action': 'CONVERT TABLE',
                        'table': table_name,
                        'sql': alter_table_sql,
                    })
                    cursor.execute(alter_table_sql)

        if not dry_run:
            conn.commit()
    finally:
        conn.close()

    return changes


def upgrade_xxgcms_database(db_conf, dry_run=False, convert_tables=False):
    """升级系统库（字符集；无零日期列）。"""
    import pymysql

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
            alter_db_sql = (
                f'ALTER DATABASE `{database}` CHARACTER SET utf8mb4 '
                f'COLLATE {MYSQL8_COLLATION}'
            )
            changes.append({
                'action': 'ALTER DATABASE',
                'database': database,
                'sql': alter_db_sql,
            })
            if not dry_run:
                _alter_database_charset(cursor, database)

            if convert_tables and not dry_run:
                cursor.execute(
                    'SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES '
                    'WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = %s',
                    (database, 'BASE TABLE'),
                )
                for (table_name,) in cursor.fetchall():
                    alter_table_sql = (
                        f'ALTER TABLE `{table_name}` '
                        f'CONVERT TO CHARACTER SET utf8mb4 COLLATE {MYSQL8_COLLATION}'
                    )
                    changes.append({
                        'action': 'CONVERT TABLE',
                        'table': table_name,
                        'sql': alter_table_sql,
                    })
                    cursor.execute(alter_table_sql)

        if not dry_run:
            conn.commit()
    finally:
        conn.close()

    return changes


def run_bundled_upgrade_sql(db_conf, dry_run=False):
    """执行 sql/mysql8_upgrade.sql（补充性脚本，可选）。"""
    sql_path = PROJECT_SQL_DIR / 'mysql8_upgrade.sql'
    if not sql_path.is_file():
        return []
    if dry_run:
        return [{'action': 'EXEC SQL FILE', 'sql': str(sql_path)}]
    execute_sql_file(db_conf, sql_path)
    return [{'action': 'EXEC SQL FILE', 'sql': str(sql_path)}]
