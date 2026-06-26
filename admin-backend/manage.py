#!/usr/bin/env python
import os
import sys
from pathlib import Path

if __name__ == '__main__':
    admin_root = Path(__file__).resolve().parent
    website_root = admin_root.parent / 'website'

    from apps.api.utils.env_bootstrap import ensure_monorepo_env

    ensure_monorepo_env(admin_root, website_root if website_root.is_dir() else None)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.settings.dev')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
