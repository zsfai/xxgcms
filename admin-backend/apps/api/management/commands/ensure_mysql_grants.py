# coding: utf-8
import os

from django.core.management.base import BaseCommand

from apps.api.utils.sql_init import ensure_app_user_grants


class Command(BaseCommand):
    help = '修复 xxgcms MySQL 应用账号权限（新增站点 site_conf SELECT denied 时执行）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cms-db',
            type=str,
            default='',
            help='CMS 库名，默认 XXGCMS_CMS_DB_NAME（xxgai）',
        )

    def handle(self, *args, **options):
        root_password = (os.environ.get('XXGCMS_MYSQL_ROOT_PASSWORD') or '').strip()
        if not root_password:
            self.stderr.write(self.style.ERROR('未设置 XXGCMS_MYSQL_ROOT_PASSWORD，无法修复权限'))
            return

        host = os.environ.get('XXGCMS_DB_HOST', 'mysql')
        port = int(os.environ.get('XXGCMS_DB_PORT', '3306'))
        app_user = os.environ.get('XXGCMS_DB_USER', 'xxgcms')
        sys_db = os.environ.get('XXGCMS_DB_NAME', 'xxgcms')
        cms_db = options['cms_db'] or os.environ.get('XXGCMS_CMS_DB_NAME', 'xxgai')

        import pymysql

        grants_sql = f"""
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER,
      CREATE TEMPORARY TABLES, LOCK TABLES, EXECUTE, CREATE VIEW,
      SHOW VIEW, CREATE ROUTINE, ALTER ROUTINE, TRIGGER, REFERENCES, RELOAD
ON *.* TO '{app_user.replace("'", "''")}'@'%';
FLUSH PRIVILEGES;
"""
        conn = pymysql.connect(
            host=host,
            port=port,
            user='root',
            password=root_password,
            charset='utf8mb4',
            connect_timeout=10,
        )
        try:
            with conn.cursor() as cursor:
                for statement in grants_sql.strip().split(';'):
                    stmt = statement.strip()
                    if stmt:
                        cursor.execute(stmt)
            conn.commit()
        finally:
            conn.close()

        ensure_app_user_grants(host, port, sys_db, app_user, root_password)
        ensure_app_user_grants(host, port, cms_db, app_user, root_password)

        self.stdout.write(self.style.SUCCESS(
            f'已修复 MySQL 权限：{app_user}@*（含全局 DML/DDL 及 {sys_db}、{cms_db} 库）'
        ))
