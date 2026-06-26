# coding: utf-8
import os
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.api.utils.env_bootstrap import ensure_monorepo_env, write_credentials_file


class Command(BaseCommand):
    help = '一键初始化：生成 .env、初始化数据库、创建管理员'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-db',
            action='store_true',
            help='仅生成 .env，不初始化数据库',
        )
        parser.add_argument(
            '--skip-admin',
            action='store_true',
            help='不创建/重置管理员账号',
        )

    def handle(self, *args, **options):
        admin_root = Path(__file__).resolve().parents[4]
        website_root = admin_root.parent / 'website'

        admin_env, admin_keys, website_keys, website_env = ensure_monorepo_env(
            admin_root,
            website_root if website_root.is_dir() else None,
        )
        self.stdout.write(self.style.SUCCESS('环境配置已就绪'))
        if admin_keys:
            self.stdout.write(f'  后台新生成: {", ".join(admin_keys)}')

        if options['skip_db']:
            return

        call_command('init_db')
        call_command('fix_site_paths')

        if options['skip_admin']:
            return

        admin_user = os.environ.get('XXGCMS_ADMIN_USER', 'xxgcmsadmin')
        admin_pwd = os.environ.get('XXGCMS_ADMIN_PASSWORD', '')
        if not admin_pwd:
            self.stdout.write(self.style.ERROR('XXGCMS_ADMIN_PASSWORD 未配置，请先运行 init_env'))
            return

        call_command('create_xxgcms_user', admin_user, admin_pwd)

        cred_path = write_credentials_file(admin_root)
        self.stdout.write(self.style.SUCCESS(f'部署凭据已写入 {cred_path}'))
