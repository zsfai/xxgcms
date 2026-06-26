# coding: utf-8
from django.core.management.base import BaseCommand

from apps.api.utils.env_bootstrap import CREDENTIALS_SAVE_REMINDER, ensure_credentials_file


class Command(BaseCommand):
    help = '查看部署凭据（含保存提醒）'

    def handle(self, *args, **options):
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('=' * 62))
        for line in CREDENTIALS_SAVE_REMINDER:
            text = line.lstrip('# ').strip()
            if text.startswith('═'):
                continue
            self.stdout.write(self.style.WARNING(f'  {text}'))
        self.stdout.write(self.style.WARNING('=' * 62))
        self.stdout.write('')

        try:
            cred_path = ensure_credentials_file()
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f'无法生成凭据文件: {exc}'))
            self.stderr.write('请确认 backend 已完成 setup，且 .env / compose 环境变量已配置。')
            return

        if not cred_path.is_file():
            self.stderr.write(self.style.ERROR(f'凭据文件不存在: {cred_path}'))
            return

        self.stdout.write(cred_path.read_text(encoding='utf-8'))
