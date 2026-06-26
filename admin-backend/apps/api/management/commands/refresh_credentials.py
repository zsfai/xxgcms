# coding: utf-8
from django.core.management.base import BaseCommand

from apps.api.utils.env_bootstrap import admin_project_root, apply_env_file, write_credentials_file


class Command(BaseCommand):
    help = '根据当前 .env / 环境变量刷新 /app/.credentials 部署凭据文件'

    def handle(self, *args, **options):
        admin_root = admin_project_root()
        env_path = admin_root / '.env'
        if env_path.is_file():
            apply_env_file(env_path)
        cred_path = write_credentials_file(admin_root)
        self.stdout.write(self.style.SUCCESS(f'已写入 {cred_path}'))
