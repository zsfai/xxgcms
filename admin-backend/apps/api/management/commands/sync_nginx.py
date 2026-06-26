# coding: utf-8
from django.core.management.base import BaseCommand

from apps.api.service import domain_ssl_service


class Command(BaseCommand):
    help = '从 site 表全量重建 /data/config/nginx/sites/*.conf 并触发 Nginx reload'

    def handle(self, *args, **options):
        count = domain_ssl_service.sync_all_enabled_sites()
        self.stdout.write(self.style.SUCCESS(f'已同步 {count} 个站点 SSL 配置'))
