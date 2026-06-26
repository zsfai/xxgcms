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
    'XXGCMS_MYSQL_ROOT_PASSWORD',
    'XXGCMS_ADMIN_PASSWORD',
    'WEBSITE_SECRET_KEY',
})


def _django_secret_key():
    alphabet = string.ascii_letters + string.digits + '!@#%^&*(-_=+)'
    return ''.join(secrets.choice(alphabet) for _ in range(50))


def _random_token():
    return secrets.token_urlsafe(24)


def _random_readable_password(length=12):
    """较短但含大小写、数字、符号，便于抄写仍有一定强度。"""
    if length < 8:
        length = 8
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    special = '!@#%&*_-'  # 不含 $，避免 Docker Compose .env 误解析
    pools = (lower, upper, digits, special)
    chars = [secrets.choice(pool) for pool in pools]
    all_chars = lower + upper + digits + special
    chars.extend(secrets.choice(all_chars) for _ in range(length - len(chars)))
    secrets.SystemRandom().shuffle(chars)
    return ''.join(chars)


def generate_value(key):
    if key.endswith('SECRET_KEY'):
        return _django_secret_key()
    if key == 'XXGCMS_ADMIN_PASSWORD':
        return _random_readable_password(12)
    if key in ('XXGCMS_DB_PASSWORD', 'XXGCMS_MYSQL_ROOT_PASSWORD'):
        return _random_readable_password(12)
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
        return env_path, False

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


def ensure_monorepo_env(admin_root, website_root=None):
    admin_env, admin_keys = ensure_env_file(admin_root)
    apply_env_file(admin_env)

    if not website_root:
        return admin_env, admin_keys, [], None

    website_root = Path(website_root)
    website_env, website_keys = ensure_env_file(website_root)

    # 与后台共用数据库密码，避免两边配置不一致
    admin_data = parse_env_file(admin_env)
    website_data = parse_env_file(website_env)
    shared_keys = ('XXGCMS_DB_HOST', 'XXGCMS_DB_PORT', 'XXGCMS_DB_USER', 'XXGCMS_DB_PASSWORD', 'XXGCMS_DB_NAME')
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
        (website_root / '.env').write_text('\n'.join(lines) + '\n', encoding='utf-8')
        website_keys = list(set(website_keys + list(shared_keys)))

    apply_env_file(website_root / '.env')
    return admin_env, admin_keys, website_keys, website_root / '.env'


def build_deployment_credentials():
    """从当前环境变量汇总部署凭据（供 .credentials 展示）。"""

    def env(key, default=''):
        return (os.environ.get(key) or default).strip()

    return {
        'admin_user': env('XXGCMS_ADMIN_USER', 'xxgcmsadmin'),
        'admin_password': env('XXGCMS_ADMIN_PASSWORD'),
        'db_host': env('XXGCMS_DB_HOST', '127.0.0.1'),
        'db_port': env('XXGCMS_DB_PORT', '3306'),
        'db_user': env('XXGCMS_DB_USER', 'xxgcms'),
        'db_password': env('XXGCMS_DB_PASSWORD'),
        'db_name': env('XXGCMS_DB_NAME', 'xxgcms'),
        'mysql_root_password': env('XXGCMS_MYSQL_ROOT_PASSWORD'),
        'cms_db_name': env('XXGCMS_CMS_DB_NAME', 'xxgai'),
        'cms_site_name': env('XXGCMS_CMS_SITE_NAME', 'test'),
        'media_dir': env('XXGCMS_MEDIA_DIR'),
    }


CREDENTIALS_SAVE_REMINDER = [
    '# ═══════════════════════════════════════════════════════════════',
    '# 【重要】请立即将下方凭据复制到安全位置妥善保存！',
    '#   - 含管理后台密码、MySQL 应用密码、MySQL root 密码等',
    '#   - 容器重建或未备份 .env 时无法找回，只能重置',
    '#   - 切勿提交 Git 或发送到公开渠道',
    '# ═══════════════════════════════════════════════════════════════',
]

CREDENTIALS_VIEW_HINT = (
    'docker compose -f docker-compose.offline.yml exec backend '
    'python manage.py show_credentials'
)


def admin_project_root():
    """admin-backend 项目根（Docker 内为 /app）。"""
    try:
        from django.conf import settings
        return Path(settings.PROJECT_DIR)
    except Exception:
        return Path(__file__).resolve().parents[3]


def ensure_credentials_file(project_dir=None):
    """确保 .credentials 存在：优先配置卷，否则按 .env / 环境变量生成。"""
    root = Path(project_dir) if project_dir else admin_project_root()
    cred_path = root / '.credentials'
    if cred_path.is_file():
        return cred_path

    config_cred = Path(os.environ.get('CONFIG_DIR', '/data/config')) / '.credentials'
    if config_cred.is_file():
        cred_path.write_text(config_cred.read_text(encoding='utf-8'), encoding='utf-8')
        return cred_path

    env_path = root / '.env'
    if env_path.is_file():
        apply_env_file(env_path)

    return write_credentials_file(root)


def format_credentials_content(data):
    lines = [
        '# xxg-cms 部署凭据（自动生成，请勿提交 Git）',
        f'# 查看: {CREDENTIALS_VIEW_HINT}',
        f'# 或:   docker compose -f docker-compose.offline.yml exec backend cat /app/.credentials',
        *CREDENTIALS_SAVE_REMINDER,
        '',
        '======== 管理后台登录 ========',
        f'账号: {data["admin_user"]}',
        f'密码: {data["admin_password"]}',
        '',
        '======== MySQL 连接（新建站点时可填写） ========',
        f'主机: {data["db_host"]}',
        f'端口: {data["db_port"]}',
        f'用户: {data["db_user"]}',
        f'密码: {data["db_password"]}',
        '',
        '======== MySQL root（仅容器维护，非日常使用） ========',
        f'密码: {data.get("mysql_root_password") or "(见 .env XXGCMS_MYSQL_ROOT_PASSWORD)"}',
        '',
        '======== 系统库 / 默认站点 ========',
        f'系统库名: {data["db_name"]}',
        f'默认站点标识: {data["cms_site_name"]}',
        f'默认 CMS 库名: {data["cms_db_name"]}',
    ]
    if data.get('media_dir'):
        lines.append(f'媒体目录: {data["media_dir"]}')
    lines.extend([
        '',
        '# 新建站点时，源库与目标库通常共用上述 MySQL 主机/端口/账号/密码，库名按需填写',
    ])
    return '\n'.join(lines)


def write_credentials_file(project_dir, entries=None):
    cred_path = Path(project_dir) / '.credentials'
    data = build_deployment_credentials()
    if entries:
        legacy_map = {
            'XXGCMS_ADMIN_USER': 'admin_user',
            'XXGCMS_ADMIN_PASSWORD': 'admin_password',
        }
        for key, value in entries.items():
            field = legacy_map.get(key, key)
            if field in data:
                data[field] = value
    cred_path.write_text(format_credentials_content(data) + '\n', encoding='utf-8')
    return cred_path
