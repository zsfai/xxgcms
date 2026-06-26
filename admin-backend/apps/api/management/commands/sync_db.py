# coding: utf-8
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.api.db.connection import xxgcms_connection
from apps.api.sql_mapper.base_mapper import BaseMapper
from apps.api.utils.schema_sync import sync_schema
from apps.api.utils.sql_init import PROJECT_SQL_DIR, default_db_conf, ensure_database


class Command(BaseCommand):
    help = (
        '增量同步数据库结构：以 sql/xxgcms.sql、sql/cmsdb.sql 为准，'
        '自动创建缺失的表、添加缺失的字段（不删字段、不改类型）'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--xxgcms',
            action='store_true',
            help='仅同步 xxgcms 系统库',
        )
        parser.add_argument(
            '--cms',
            action='store_true',
            help='仅同步 CMS 站点库',
        )
        parser.add_argument(
            '--cms-db',
            type=str,
            default='',
            help='CMS 库名，默认 XXGCMS_CMS_DB_NAME（xxgai）',
        )
        parser.add_argument(
            '--all-sites',
            action='store_true',
            help='同步 xxgcms.site 中登记的全部 CMS 库（db_x_name）',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只打印将要执行的变更，不写库',
        )

    def handle(self, *args, **options):
        sync_xxgcms = options['xxgcms']
        sync_cms = options['cms']
        if not sync_xxgcms and not sync_cms:
            sync_xxgcms = sync_cms = True

        db = settings.XXGCMS_DB
        host = db['host']
        port = db['port']
        user = db['user']
        password = db['password']
        dry_run = options['dry_run']
        total_changes = 0

        if sync_xxgcms:
            xxgcms_db = db['database']
            ensure_database(host, port, user, password, xxgcms_db)
            total_changes += self._sync_one(
                default_db_conf(host, port, user, password, xxgcms_db),
                PROJECT_SQL_DIR / 'xxgcms.sql',
                f'系统库 {xxgcms_db}',
                dry_run,
            )

        if sync_cms:
            if options['all_sites']:
                for cms_target in self._iter_site_cms_databases():
                    ensure_database(
                        cms_target['host'],
                        cms_target['port'],
                        cms_target['user'],
                        cms_target['password'],
                        cms_target['database'],
                    )
                    total_changes += self._sync_one(
                        cms_target,
                        PROJECT_SQL_DIR / 'cmsdb.sql',
                        f"CMS 库 {cms_target['database']} @ {cms_target['host']}",
                        dry_run,
                    )
            else:
                cms_db = options['cms_db'] or os.environ.get('XXGCMS_CMS_DB_NAME', 'xxgai')
                ensure_database(host, port, user, password, cms_db)
                total_changes += self._sync_one(
                    default_db_conf(host, port, user, password, cms_db),
                    PROJECT_SQL_DIR / 'cmsdb.sql',
                    f'CMS 库 {cms_db}',
                    dry_run,
                )

        if total_changes == 0:
            self.stdout.write(self.style.SUCCESS('结构已是最新，无需变更'))
        elif dry_run:
            self.stdout.write(self.style.WARNING(f'预览完成，共 {total_changes} 项待执行'))
        else:
            self.stdout.write(self.style.SUCCESS(f'同步完成，共执行 {total_changes} 项变更'))

    def _sync_one(self, db_conf, sql_path, label, dry_run):
        self.stdout.write(f'检查 {label} ...')
        changes = sync_schema(db_conf, sql_path, dry_run=dry_run)
        for change in changes:
            if change['action'] == 'CREATE TABLE':
                self.stdout.write(f"  + CREATE TABLE `{change['table']}`")
            else:
                self.stdout.write(
                    f"  + ALTER TABLE `{change['table']}` ADD `{change['column']}`"
                )
            if dry_run:
                self.stdout.write(f"    {change['sql']}")
        return len(changes)

    def _iter_site_cms_databases(self):
        seen = set()
        with xxgcms_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(BaseMapper.select_site_list_without_user())
                for site in cursor.fetchall():
                    database = (site.get('db_x_name') or '').strip()
                    if not database:
                        continue
                    key = (
                        site.get('db_x_host', '127.0.0.1'),
                        int(site.get('db_x_port') or 3306),
                        site.get('db_x_user', ''),
                        site.get('db_x_pwd', ''),
                        database,
                    )
                    if key in seen:
                        continue
                    seen.add(key)
                    yield default_db_conf(*key)
