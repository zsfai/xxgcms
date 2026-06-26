#!/usr/bin/env python
# coding: utf-8
"""创建小西瓜CMS用户。用法: python scripts/create_user.py <用户名> <密码>"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

env_file = ROOT / '.env'
if env_file.exists():
    for line in env_file.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        os.environ[key.strip()] = value.strip()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.settings.dev')

import django

django.setup()

from django.core.management import call_command

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('用法: python scripts/create_user.py <用户名> <密码>')
        sys.exit(1)
    call_command('create_xxgcms_user', sys.argv[1], sys.argv[2])
