# coding: utf-8
import os

from django.core.management.base import BaseCommand

from apps.api.utils.site_db_init import _ensure_site_conf
from apps.api.utils.sql_init import default_db_conf


class Command(BaseCommand):
    help = '补全 CMS 库 site_conf（Docker 前台 500 时可用）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--site-name',
            type=str,
            default='',
            help='站点标识，默认 XXGCMS_CMS_SITE_NAME',
        )
        parser.add_argument(
            '--cms-db',
            type=str,
            default='',
            help='CMS 库名，默认 XXGCMS_CMS_DB_NAME',
        )

    def handle(self, *args, **options):
        site_name = options['site_name'] or os.environ.get('XXGCMS_CMS_SITE_NAME', 'localhost')
        cms_db = options['cms_db'] or os.environ.get('XXGCMS_CMS_DB_NAME', 'xxgai')
        host = os.environ.get('XXGCMS_DB_HOST', '127.0.0.1')
        port = os.environ.get('XXGCMS_DB_PORT', '3306')
        user = os.environ.get('XXGCMS_DB_USER', 'root')
        password = os.environ.get('XXGCMS_DB_PASSWORD', '')

        cms_conf = default_db_conf(host, port, user, password, cms_db)
        _ensure_site_conf(cms_conf, site_name)
        self.stdout.write(self.style.SUCCESS(
            f'已确保 site_conf 存在: domain={site_name}, theme={os.environ.get("XXGCMS_DEFAULT_THEME", "www_xxg_ai")}'
        ))
