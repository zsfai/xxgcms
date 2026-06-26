# coding: utf-8
from django.core.management.base import BaseCommand

from apps.api.db.connection import xxgcms_connection
from apps.api.utils.public import normalize_site_root_path


class Command(BaseCommand):
    help = '修正站点 root_path（Docker 部署应为 MEDIA_ROOT 下相对路径，如 localhost）'

    def handle(self, *args, **options):
        fixed = 0
        with xxgcms_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, name, root_path FROM site WHERE del_flag = 'N'")
                for row in cursor.fetchall():
                    site_name = row.get('name') or ''
                    old_root = row.get('root_path') or ''
                    new_root = normalize_site_root_path(old_root, fallback_site_name=site_name)
                    if old_root != new_root:
                        cursor.execute(
                            'UPDATE site SET root_path = %s WHERE id = %s',
                            (new_root, row['id']),
                        )
                        fixed += 1
                        self.stdout.write(
                            f"  {site_name}: {old_root!r} -> {new_root!r}"
                        )
            conn.commit()

        if fixed:
            self.stdout.write(self.style.SUCCESS(f'已修正 {fixed} 个站点的 root_path'))
        else:
            self.stdout.write('所有站点 root_path 正常，无需修改')
