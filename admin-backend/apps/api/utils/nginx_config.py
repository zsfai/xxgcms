# coding: utf-8
"""Nginx 站点 SSL 配置生成与 config 卷落盘。"""
import os
import re
import shutil
import time
from pathlib import Path

CONFIG_DIR = Path(os.environ.get('CONFIG_DIR', '/data/config'))
NGINX_SITES_DIR = CONFIG_DIR / 'nginx' / 'sites'
CERTS_DIR = CONFIG_DIR / 'certs'
RELOAD_STAMP = CONFIG_DIR / 'nginx' / 'reload.stamp'
NGINX_ERROR_LOG = CONFIG_DIR / 'nginx' / 'last-error.log'
NGINX_RELOAD_LOG = CONFIG_DIR / 'nginx' / 'last-reload.log'

_SAFE_DOMAIN_RE = re.compile(r'^[a-zA-Z0-9._-]+$')


def ensure_layout() -> None:
    NGINX_SITES_DIR.mkdir(parents=True, exist_ok=True)
    CERTS_DIR.mkdir(parents=True, exist_ok=True)
    RELOAD_STAMP.parent.mkdir(parents=True, exist_ok=True)


def safe_domain_dir(domain: str) -> str:
    domain = (domain or '').strip()
    if not domain or not _SAFE_DOMAIN_RE.match(domain):
        raise ValueError(f'域名路径不安全或无效: {domain!r}')
    return domain


def conf_filename_for_domain(domain: str) -> str:
    return f'{safe_domain_dir(domain)}.conf'


def atomic_write(path: Path, content: str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(content, encoding='utf-8')
    os.chmod(tmp, mode)
    tmp.replace(path)


def write_cert_files(domain: str, fullchain: str, privkey: str) -> Path:
    cert_dir = CERTS_DIR / safe_domain_dir(domain)
    cert_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(cert_dir / 'fullchain.pem', fullchain.strip() + '\n', 0o644)
    atomic_write(cert_dir / 'privkey.pem', privkey.strip() + '\n', 0o600)
    return cert_dir


def cert_files_exist(domain: str) -> bool:
    cert_dir = CERTS_DIR / safe_domain_dir(domain)
    return (cert_dir / 'fullchain.pem').is_file() and (cert_dir / 'privkey.pem').is_file()


def read_cert_files(domain: str) -> tuple[str, str]:
    cert_dir = CERTS_DIR / safe_domain_dir(domain)
    fullchain = (cert_dir / 'fullchain.pem').read_text(encoding='utf-8')
    privkey = (cert_dir / 'privkey.pem').read_text(encoding='utf-8')
    return fullchain, privkey


def render_site_nginx_conf(primary_domain: str, aliases: list[str], force_https: bool) -> str:
    primary = safe_domain_dir(primary_domain)
    names = [primary] + [safe_domain_dir(a) for a in aliases if a and a != primary]
    server_names = ' '.join(names)
    cert_dir = CERTS_DIR / primary
    blocks = []
    if force_https:
        blocks.append(
            f'''server {{
    listen 80;
    server_name {server_names};
    return 301 https://$host$request_uri;
}}'''
        )
    blocks.append(
        f'''server {{
    listen 443 ssl;
    server_name {server_names};
    ssl_certificate     {cert_dir}/fullchain.pem;
    ssl_certificate_key {cert_dir}/privkey.pem;
    include /etc/nginx/snippets/xxgcms-locations.conf;
}}'''
    )
    return '\n\n'.join(blocks) + '\n'


def write_site_nginx_conf(domain: str, aliases: list[str], force_https: bool) -> Path:
    ensure_layout()
    conf_path = NGINX_SITES_DIR / conf_filename_for_domain(domain)
    content = render_site_nginx_conf(domain, aliases, force_https)
    atomic_write(conf_path, content, 0o644)
    return conf_path


def remove_site_nginx_conf(domain: str) -> None:
    conf_path = NGINX_SITES_DIR / conf_filename_for_domain(domain)
    if conf_path.is_file():
        conf_path.unlink()


def remove_site_cert_dir(domain: str) -> None:
    cert_dir = CERTS_DIR / safe_domain_dir(domain)
    if cert_dir.is_dir():
        shutil.rmtree(cert_dir, ignore_errors=True)


def remove_site_ssl_files(domain: str) -> None:
    remove_site_nginx_conf(domain)
    remove_site_cert_dir(domain)


def request_nginx_reload() -> None:
    ensure_layout()
    RELOAD_STAMP.write_text(str(time.time()), encoding='utf-8')


def read_nginx_error_tail(max_chars: int = 500) -> str:
    if not NGINX_ERROR_LOG.is_file():
        return ''
    text = NGINX_ERROR_LOG.read_text(encoding='utf-8', errors='replace')
    return text[-max_chars:].strip()
