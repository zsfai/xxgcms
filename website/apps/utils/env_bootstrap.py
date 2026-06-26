# coding: utf-8
"""首次运行时自动生成 .env 中的敏感配置。"""
import os
import secrets
import string
from pathlib import Path

PLACEHOLDER_VALUES = frozenset({'', 'change-me', '__AUTO__'})

AUTO_GENERATE_KEYS = frozenset({
    'XXGCMS_SECRET_KEY',
    'XXGCMS_AUTH_SALT',
    'XXGCMS_DB_PASSWORD',
    'XXGCMS_ADMIN_PASSWORD',
    'WEBSITE_SECRET_KEY',
})


def _django_secret_key():
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(alphabet) for _ in range(50))


def _random_token():
    return secrets.token_urlsafe(24)


def _random_readable_password(length=12):
    if length < 8:
        length = 8
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    special = '!@#%&*_-'  # 不含 $
    pools = (lower, upper, digits, special)
    chars = [secrets.choice(pool) for pool in pools]
    all_chars = lower + upper + digits + special
    chars.extend(secrets.choice(all_chars) for _ in range(length - len(chars)))
    secrets.SystemRandom().shuffle(chars)
    return ''.join(chars)


def generate_value(key):
    if key.endswith('SECRET_KEY'):
        return _django_secret_key()
    if key.endswith('PASSWORD') or key.endswith('_PWD'):
        return _random_readable_password(12)
    if key.endswith('SALT'):
        return _random_token()
    return _random_token()


def parse_env_file(path):
    data = {}
    if not path.is_file():
        return data
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        data[key.strip()] = value.strip()
    return data


def apply_env_file(path):
    if not path.is_file():
        return
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        os.environ[key.strip()] = value.strip()


def _should_generate(key, value):
    if key in AUTO_GENERATE_KEYS:
        return value in PLACEHOLDER_VALUES
    return value == '__AUTO__'


def ensure_env_file(project_dir, example_name='.env.example', env_name='.env'):
    project_dir = Path(project_dir)
    env_path = project_dir / env_name
    example_path = project_dir / example_name
    if not example_path.is_file():
        return env_path, []

    existing = parse_env_file(env_path)
    output_lines = []
    generated_keys = []
    changed = not env_path.is_file()

    for raw_line in example_path.read_text(encoding='utf-8').splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith('#') or '=' not in raw_line:
            output_lines.append(raw_line)
            continue

        key, example_val = raw_line.split('=', 1)
        key = key.strip()
        example_val = example_val.strip()

        if key in existing and not _should_generate(key, existing[key]):
            value = existing[key]
        elif _should_generate(key, example_val) or _should_generate(key, existing.get(key, example_val)):
            value = generate_value(key)
            generated_keys.append(key)
            changed = True
        elif key in existing:
            value = existing[key]
        else:
            value = example_val

        output_lines.append(f'{key}={value}')

    if changed:
        env_path.write_text('\n'.join(output_lines) + '\n', encoding='utf-8')

    return env_path, generated_keys


def bootstrap_website_env(website_root, admin_root=None):
    website_root = Path(website_root)
    env_path, keys = ensure_env_file(website_root)

    if admin_root:
        admin_root = Path(admin_root)
        admin_env = admin_root / '.env'
        if admin_env.is_file():
            admin_data = parse_env_file(admin_env)
            website_data = parse_env_file(env_path)
            shared_keys = (
                'XXGCMS_DB_HOST', 'XXGCMS_DB_PORT', 'XXGCMS_DB_USER',
                'XXGCMS_DB_PASSWORD', 'XXGCMS_DB_NAME',
            )
            sync_changed = False
            for key in shared_keys:
                if admin_data.get(key) and website_data.get(key) != admin_data.get(key):
                    website_data[key] = admin_data[key]
                    sync_changed = True
            if sync_changed:
                lines = []
                for line in (website_root / '.env.example').read_text(encoding='utf-8').splitlines():
                    stripped = line.strip()
                    if not stripped or stripped.startswith('#') or '=' not in line:
                        lines.append(line)
                        continue
                    key = line.split('=', 1)[0].strip()
                    if key in website_data:
                        lines.append(f'{key}={website_data[key]}')
                    else:
                        lines.append(line)
                env_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    apply_env_file(env_path)
    return env_path, keys
