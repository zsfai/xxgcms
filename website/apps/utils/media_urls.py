# coding: utf-8
"""正文图片 URL 补全（与 admin-backend media_save 逻辑一致）。"""
import re

from apps.utils.public import _resolve_site, ensure_site_map


def to_media_url(host: str, rel_path: str) -> str:
    rel = (rel_path or '').replace('\\', '/').strip()
    if not rel:
        return ''
    if rel.startswith('http://') or rel.startswith('https://') or rel.startswith('//'):
        return rel
    if rel.startswith('/media/'):
        return rel
    if rel.startswith('media/'):
        return '/' + rel
    ensure_site_map()
    site = _resolve_site(host)
    root = (site.get('root_path') or '').strip().strip('/') if site else ''
    rel = rel.lstrip('/')
    if root and rel.startswith('upload/files/'):
        rel = '%s/%s' % (root, rel)
    return '/media/%s' % rel


def fix_content_media_urls(html: str, host: str) -> str:
    if not html:
        return html
    ensure_site_map()
    site = _resolve_site(host)
    root = (site.get('root_path') or '').strip().strip('/') if site else ''
    if not root:
        return html

    def repl(match):
        src = match.group(1)
        if (
            src.startswith('http://')
            or src.startswith('https://')
            or src.startswith('//')
            or src.startswith('/media/')
        ):
            return match.group(0)
        if src.startswith('upload/files/'):
            return 'src="%s"' % to_media_url(host, src)
        if src.startswith('%s/upload/files/' % root):
            return 'src="/media/%s"' % src
        return match.group(0)

    return re.sub(r'src="([^"]+)"', repl, html)
