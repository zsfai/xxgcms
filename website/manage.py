#!/usr/bin/env python
import os
import sys
from pathlib import Path

if __name__ == '__main__':
    website_root = Path(__file__).resolve().parent
    admin_root = website_root.parent / 'admin-backend'

    from apps.utils.env_bootstrap import bootstrap_website_env

    bootstrap_website_env(
        website_root,
        admin_root if admin_root.is_dir() else None,
    )

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.settings.dev')

    from django.core.management import execute_from_command_line

    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == 'runserver'):
        sys.argv.append('8088')

    execute_from_command_line(sys.argv)
