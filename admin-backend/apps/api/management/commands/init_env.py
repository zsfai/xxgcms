# coding: utf-8
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.api.utils.env_bootstrap import ensure_monorepo_env


class Command(BaseCommand):
    help = '自动生成 .env 敏感配置（admin-backend + website）'

    def handle(self, *args, **options):
        admin_root = Path(__file__).resolve().parents[4]
        website_root = admin_root.parent / 'website'

        admin_env, admin_keys, website_keys, website_env = ensure_monorepo_env(
            admin_root,
            website_root if website_root.is_dir() else None,
        )

        self.stdout.write(self.style.SUCCESS(f'已处理后台配置: {admin_env}'))
        if admin_keys:
            self.stdout.write(f'  新生成: {", ".join(admin_keys)}')

        if website_env:
            self.stdout.write(self.style.SUCCESS(f'已处理前台配置: {website_env}'))
            if website_keys:
                self.stdout.write(f'  同步/生成: {", ".join(website_keys)}')
