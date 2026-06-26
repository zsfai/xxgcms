#!/usr/bin/env python3
"""Docker 部署前生成 .env 随机密钥（须在 docker compose up 之前执行）。"""
from __future__ import annotations

import re
import secrets
import string
import sys
from pathlib import Path

PLACEHOLDERS = frozenset({'', 'change-me', '__AUTO__'})

SENSITIVE_KEY_RE = re.compile(
    r'^(XXGCMS_|WEBSITE_).*(PASSWORD|SECRET_KEY|AUTH_SALT)|^XXGCMS_MYSQL_ROOT_PASSWORD$'
)

AUTO_KEYS = frozenset({
    'XXGCMS_SECRET_KEY',
    'XXGCMS_AUTH_SALT',
    'XXGCMS_DB_PASSWORD',
    'XXGCMS_MYSQL_ROOT_PASSWORD',
    'XXGCMS_ADMIN_PASSWORD',
    'WEBSITE_SECRET_KEY',
})


def _secret_key(length: int = 50) -> str:
    # 勿含 $，避免 Docker Compose .env 变量替换
    alphabet = string.ascii_letters + string.digits + '!@#%^&*(-_=+)'
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def _password(length: int = 14) -> str:
    if length < 8:
        length = 8
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    special = '!@#%&*_-'  # 不含 $，兼容 docker compose .env
    pools = (lower, upper, digits, special)
    chars = [secrets.choice(pool) for pool in pools]
    all_chars = lower + upper + digits + special
    chars.extend(secrets.choice(all_chars) for _ in range(length - len(chars)))
    secrets.SystemRandom().shuffle(chars)
    return ''.join(chars)


def _generate(key: str) -> str:
    if key.endswith('SECRET_KEY'):
        return _secret_key()
    if key in ('XXGCMS_ADMIN_PASSWORD', 'XXGCMS_DB_PASSWORD', 'XXGCMS_MYSQL_ROOT_PASSWORD'):
        return _password(12)
    if key.endswith('PASSWORD') or key.endswith('_PWD'):
        return _password(12)
    return _password(12)


def escape_compose_env_value(value: str) -> str:
    """Docker Compose 读取 .env 时会展开 $VAR；字面量 $ 须写成 $$。"""
    out: list[str] = []
    i = 0
    while i < len(value):
        if value[i] == '$':
            if i + 1 < len(value) and value[i + 1] == '$':
                out.append('$$')
                i += 2
            else:
                out.append('$$')
                i += 1
        else:
            out.append(value[i])
            i += 1
    return ''.join(out)


def _compose_line(key: str, value: str) -> str:
    if SENSITIVE_KEY_RE.match(key) or key in AUTO_KEYS:
        value = escape_compose_env_value(value)
    return f'{key}={value}'


def bootstrap_env_file(env_path: Path) -> bool:
    if not env_path.is_file():
        raise SystemExit(f'文件不存在: {env_path}')

    lines_out: list[str] = []
    changed = False
    seen_keys: set[str] = set()

    for raw_line in env_path.read_text(encoding='utf-8').splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith('#') or '=' not in raw_line:
            lines_out.append(raw_line)
            continue

        key, value = raw_line.split('=', 1)
        key = key.strip()
        value = value.strip()
        seen_keys.add(key)

        if key == 'XXGCMS_DB_USER' and value.lower() == 'root':
            value = 'xxgcms'
            changed = True
        elif key in AUTO_KEYS and value in PLACEHOLDERS:
            value = _generate(key)
            changed = True

        lines_out.append(f'{key}={value}')

    if 'XXGCMS_MYSQL_ROOT_PASSWORD' not in seen_keys:
        lines_out.append(f'XXGCMS_MYSQL_ROOT_PASSWORD={_password(12)}')
        changed = True

    original_text = env_path.read_text(encoding='utf-8')
    fixed: list[str] = []
    for line in lines_out:
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or '=' not in line:
            fixed.append(line)
            continue
        k, v = line.split('=', 1)
        k = k.strip()
        v = v.strip()
        if SENSITIVE_KEY_RE.match(k) or k in AUTO_KEYS:
            fixed.append(_compose_line(k, v))
        else:
            fixed.append(line)
    lines_out = fixed
    new_text = '\n'.join(lines_out) + '\n'
    if new_text != original_text:
        changed = True

    if changed:
        env_path.write_text(new_text, encoding='utf-8')
    return changed


def main() -> None:
    env_path = Path(sys.argv[1] if len(sys.argv) > 1 else '.env').resolve()
    if bootstrap_env_file(env_path):
        print(f'[bootstrap-env] 已生成随机密钥: {env_path}')
    else:
        print(f'[bootstrap-env] 无需变更: {env_path}')


if __name__ == '__main__':
    main()
