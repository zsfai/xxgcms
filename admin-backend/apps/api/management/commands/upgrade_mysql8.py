# coding: utf-8
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.api.utils.mysql8_upgrade import (
    upgrade_cms_database,
    upgrade_xxgcms_database,
)
from apps.api.utils.public import ensure_site_map
from apps.api.utils.sql_init import default_db_conf


class Command(BaseCommand):
    help = '将 MySQL 5.7 遗留库升级为 MySQL 8.0 兼容（零日期、utf8mb4 字符集）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--xxgcms',
            action='store_true',
            help='仅升级系统库',
        )
        parser.add_argument(
            '--cms',
            action='store_true',
            help='仅升级默认 CMS 库（XXGCMS_CMS_DB_NAME）',
        )
        parser.add_argument(
            '--all-sites',
            action='store_true',
            help='升级 site 表中全部站点的 db_x 库',
        )
        parser.add_argument(
            '--cms-db',
            type=str,
            default='',
            help='指定 CMS 库名',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅预览将执行的变更',
        )
        parser.add_argument(
            '--convert-tables',
            action='store_true',
            help='同时将所有表转换为 utf8mb4_unicode_ci（耗时，大库慎用）',
        )

    def handle(self, *args, **options):
        upgrade_xxgcms = options['xxgcms']
        upgrade_cms = options['cms']
        if not upgrade_xxgcms and not upgrade_cms and not options['all_sites']:
            upgrade_xxgcms = upgrade_cms = True

        db = settings.XXGCMS_DB
        host = db['host']
        port = db['port']
        user = db['user']
        password = db['password']
        dry_run = options['dry_run']
        convert_tables = options['convert_tables']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN：不会写入数据库'))

        total_changes = 0

        if upgrade_xxgcms:
            xxgcms_db = db['database']
            self.stdout.write(f'升级系统库 {xxgcms_db} ...')
            conf = default_db_conf(host, port, user, password, xxgcms_db)
            changes = upgrade_xxgcms_database(
                conf, dry_run=dry_run, convert_tables=convert_tables,
            )
            total_changes += self._print_changes(changes)

        cms_targets = []
        if options['all_sites']:
            ensure_site_map()
            from apps.api.utils.base_conf import SITE_MAP

            for site in SITE_MAP.values():
                db_name = (site.get('db_x_name') or '').strip()
                if db_name:
                    cms_targets.append(db_name)
            cms_targets = sorted(set(cms_targets))
        elif upgrade_cms:
            cms_db = options['cms_db'] or os.environ.get('XXGCMS_CMS_DB_NAME', 'xxgai')
            cms_targets = [cms_db]

        for cms_db in cms_targets:
            self.stdout.write(f'升级 CMS 库 {cms_db} ...')
            conf = default_db_conf(host, port, user, password, cms_db)
            changes = upgrade_cms_database(
                conf, dry_run=dry_run, convert_tables=convert_tables,
            )
            total_changes += self._print_changes(changes)

        if options['cms_db'] and not options['all_sites'] and not upgrade_cms:
            cms_db = options['cms_db']
            self.stdout.write(f'升级 CMS 库 {cms_db} ...')
            conf = default_db_conf(host, port, user, password, cms_db)
            changes = upgrade_cms_database(
                conf, dry_run=dry_run, convert_tables=convert_tables,
            )
            total_changes += self._print_changes(changes)

        if total_changes == 0:
            self.stdout.write(self.style.WARNING('未发现需要升级的项（或目标库不存在）'))
        else:
            label = '预览' if dry_run else '完成'
            self.stdout.write(self.style.SUCCESS(f'MySQL 8.0 升级{label}，共 {total_changes} 项变更'))

    def _print_changes(self, changes):
        for item in changes:
            action = item.get('action', '')
            table = item.get('table', '')
            column = item.get('column', '')
            database = item.get('database', '')
            detail = table or database or ''
            if column:
                detail = f'{detail}.{column}'
            self.stdout.write(f'  [{action}] {detail}')
            if item.get('sql'):
                self.stdout.write(f'    {item["sql"]}')
        return len(changes)
