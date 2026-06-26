# coding: utf-8
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from apps.api.db.connection import xxgcms_connection
from apps.api.sql_mapper.base_mapper import BaseMapper
from apps.api.service import base_service


class Command(BaseCommand):
    help = '创建或重置 小西瓜CMS 后台用户'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='用户名')
        parser.add_argument('password', type=str, help='密码')

    def handle(self, *args, **options):
        name = options['username']
        pwd = options['password']
        hashed = make_password(pwd)

        with xxgcms_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(BaseMapper.select_user_by_name(), (name,))
                existing = cursor.fetchone()
                if existing:
                    cursor.execute(
                        'UPDATE user SET user_pwd=%s, status=1 WHERE user_name=%s',
                        (hashed, name),
                    )
                    conn.commit()
                    self.stdout.write(self.style.WARNING(f'用户 {name} 已存在，密码已重置'))
                else:
                    base_service.add_user(name, pwd)
                    self.stdout.write(self.style.SUCCESS(f'用户 {name} 创建成功'))

        self.stdout.write(f'登录账号: {name}  密码: {pwd}')
