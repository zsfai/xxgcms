# coding: utf-8
import os

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from apps.api.db.connection import xxgcms_connection
from apps.api.service import base_service
from apps.api.sql_mapper.base_mapper import BaseMapper
from apps.api.utils.env_bootstrap import write_credentials_file
from apps.api.utils.public import default_site_root_path, normalize_site_root_path
from apps.api.utils.site_db_init import _ensure_site_conf
from apps.api.utils.sql_init import (
    PROJECT_SQL_DIR,
    default_db_conf,
    ensure_database,
    execute_sql_file,
)


class Command(BaseCommand):
    help = '初始化 xxgcms 系统库与 CMS 站点库（执行 sql/ 目录下的 SQL 脚本）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='初始化系统库与 CMS 库（默认行为）',
        )
        parser.add_argument(
            '--xxgcms',
            action='store_true',
            help='仅初始化 xxgcms 系统库（sql/xxgcms.sql）',
        )
        parser.add_argument(
            '--cms',
            action='store_true',
            help='仅初始化 CMS 站点库（sql/cmsdb.sql）',
        )
        parser.add_argument(
            '--cms-db',
            type=str,
            default='',
            help='CMS 库名，默认读取环境变量 XXGCMS_CMS_DB_NAME（xxgai）',
        )
        parser.add_argument(
            '--site-name',
            type=str,
            default='',
            help='测试站点标识，默认读取环境变量 XXGCMS_CMS_SITE_NAME（test）',
        )
        parser.add_argument(
            '--skip-site',
            action='store_true',
            help='不写入 xxgcms.site 测试站点记录',
        )

    def handle(self, *args, **options):
        init_xxgcms = options['xxgcms']
        init_cms = options['cms']
        if not init_xxgcms and not init_cms:
            init_xxgcms = init_cms = True

        db = settings.XXGCMS_DB
        host = db['host']
        port = db['port']
        user = db['user']
        password = db['password']

        if init_xxgcms:
            xxgcms_db = db['database']
            self.stdout.write(f'初始化系统库 {xxgcms_db} @ {host}:{port} ...')
            ensure_database(host, port, user, password, xxgcms_db)
            execute_sql_file(
                default_db_conf(host, port, user, password, xxgcms_db),
                PROJECT_SQL_DIR / 'xxgcms.sql',
            )
            self.stdout.write(self.style.SUCCESS(f'系统库 {xxgcms_db} 初始化完成'))
            self._ensure_admin_user()

        if init_cms:
            cms_db = options['cms_db'] or os.environ.get('XXGCMS_CMS_DB_NAME', 'xxgai')
            site_name = options['site_name'] or os.environ.get('XXGCMS_CMS_SITE_NAME', 'test')
            self.stdout.write(f'初始化 CMS 库 {cms_db} @ {host}:{port} ...')
            ensure_database(host, port, user, password, cms_db)
            execute_sql_file(
                default_db_conf(host, port, user, password, cms_db),
                PROJECT_SQL_DIR / 'cmsdb.sql',
            )
            self.stdout.write(self.style.SUCCESS(f'CMS 库 {cms_db} 初始化完成'))
            cms_conf = default_db_conf(host, port, user, password, cms_db)
            _ensure_site_conf(cms_conf, site_name)
            self.stdout.write(self.style.SUCCESS(f'已写入 CMS 站点配置 site_conf（domain={site_name}）'))

            if not options['skip_site']:
                self._ensure_test_site(site_name, cms_db, host, port, user, password)

        self.stdout.write(self.style.SUCCESS('数据库初始化全部完成'))

    def _ensure_admin_user(self):
        admin_user = os.environ.get('XXGCMS_ADMIN_USER', 'xxgcmsadmin')
        admin_pwd = os.environ.get('XXGCMS_ADMIN_PASSWORD', '')
        if not admin_pwd:
            self.stdout.write(self.style.WARNING('XXGCMS_ADMIN_PASSWORD 未设置，跳过管理员创建'))
            return

        hashed = make_password(admin_pwd)
        with xxgcms_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    'SELECT id FROM user WHERE user_name = %s LIMIT 1',
                    (admin_user,),
                )
                existing = cursor.fetchone()
                if existing:
                    cursor.execute(
                        'UPDATE user SET user_pwd=%s, status=1 WHERE user_name=%s',
                        (hashed, admin_user),
                    )
                    conn.commit()
                    self.stdout.write(self.style.WARNING(f'管理员 {admin_user} 已存在，密码已同步为 .env 中的值'))
                else:
                    base_service.add_user(admin_user, admin_pwd)
                    self.stdout.write(self.style.SUCCESS(f'管理员 {admin_user} 已创建'))

        from pathlib import Path
        admin_root = Path(__file__).resolve().parents[4]
        cred_path = write_credentials_file(admin_root)
        self.stdout.write(f'部署凭据已写入 {cred_path}')

    def _ensure_test_site(self, site_name, cms_db, host, port, user, password):
        root_path = default_site_root_path(site_name)
        with xxgcms_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    'SELECT id, root_path FROM site WHERE name = %s AND del_flag = %s',
                    (site_name, 'N'),
                )
                existing = cursor.fetchone()
                if existing:
                    old_root = (existing.get('root_path') or '').strip()
                    new_root = normalize_site_root_path(old_root, fallback_site_name=site_name)
                    if old_root != new_root:
                        cursor.execute(
                            'UPDATE site SET root_path = %s WHERE id = %s',
                            (new_root, existing['id']),
                        )
                        conn.commit()
                        self.stdout.write(self.style.WARNING(
                            f'站点 {site_name} root_path 已修正: {old_root!r} -> {new_root!r}'
                        ))
                    else:
                        self.stdout.write(self.style.WARNING(f'测试站点 {site_name} 已存在，跳过写入'))
                    _ensure_site_conf(
                        default_db_conf(host, port, user, password, cms_db),
                        site_name,
                    )
                    return

                cursor.execute(BaseMapper.insert_site(), (
                    site_name,
                    root_path,
                    '',
                    host,
                    port,
                    cms_db,
                    user,
                    password,
                    host,
                    port,
                    cms_db,
                    user,
                    password,
                    1,
                    '本地测试站点（init_db 自动创建）',
                ))
                site_id = cursor.lastrowid

                cursor.execute('SELECT id FROM user WHERE user_name = %s LIMIT 1', ('xxgcmsadmin',))
                admin = cursor.fetchone()
                if not admin:
                    admin_user = os.environ.get('XXGCMS_ADMIN_USER', 'xxgcmsadmin')
                    cursor.execute(
                        'SELECT id FROM user WHERE user_name = %s LIMIT 1',
                        (admin_user,),
                    )
                    admin = cursor.fetchone()
                if admin:
                    cursor.execute(BaseMapper.insert_site_user(), (admin['id'], site_id))
                conn.commit()

        self.stdout.write(self.style.SUCCESS(
            f'已创建测试站点 {site_name}，CMS 库 {cms_db}，并关联用户 xxgcmsadmin'
        ))
