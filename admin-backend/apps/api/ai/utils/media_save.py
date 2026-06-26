# coding: utf-8
import random
import re

import arrow
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from apps.api.utils.base_conf import SITE_MAP
from apps.api.utils.public import ensure_site_map, normalize_site_root_path


def _get_site_root_path(site_name: str) -> str:
    ensure_site_map()
    site = SITE_MAP.get(site_name, {})
    return normalize_site_root_path(site.get('root_path') or '', fallback_site_name=site_name)


def rel_upload_path(site_name: str, path: str) -> str:
    """将 upload/files/... 补全为站点根路径下的相对路径（xxb_ai/upload/files/...）。"""
    rel = (path or '').replace('\\', '/').strip().lstrip('/')
    if not rel:
        return rel
    root = _get_site_root_path(site_name)
    if root and rel.startswith('upload/files/'):
        return '%s/%s' % (root, rel)
    return rel


def to_media_url(site_name: str, rel_path: str) -> str:
    """生成后台/前台均可访问的 /media/... 路径。"""
    rel = (rel_path or '').replace('\\', '/').strip()
    if not rel:
        return ''
    if rel.startswith('http://') or rel.startswith('https://') or rel.startswith('//'):
        return rel
    if rel.startswith('/media/'):
        return rel
    if rel.startswith('media/'):
        return '/' + rel
    rel = rel.lstrip('/')
    rel = rel_upload_path(site_name, rel)
    return '/media/%s' % rel


def fix_content_media_urls(html: str, site_name: str) -> str:
    """修复正文里缺少 root_path 或 /media 前缀的图片地址。"""
    if not html:
        return html
    root = _get_site_root_path(site_name)
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
            return 'src="%s"' % to_media_url(site_name, src)
        if src.startswith('%s/upload/files/' % root):
            return 'src="/media/%s"' % src
        return match.group(0)

    return re.sub(r'src="([^"]+)"', repl, html)


def save_ai_image(site_name: str, image_bytes: bytes, ext: str = 'png') -> str:
    ensure_site_map()
    site = SITE_MAP.get(site_name, {})
    root_path = normalize_site_root_path(site.get('root_path', ''), fallback_site_name=site_name)
    if not root_path:
        raise ValueError('站点 root_path 未配置')
    now = arrow.now()
    dir_name = '%s/%s' % (now.format('YY'), now.format('MM'))
    file_name = '%s_%s' % (int(now.timestamp()), str(random.random()).replace('.', '')[:8])
    path = '%s/upload/files/%s/%s.%s' % (root_path, dir_name, file_name, ext)
    default_storage.save(path, ContentFile(image_bytes))
    rel = path
    if rel.startswith(root_path + '/'):
        rel = rel[len(root_path) + 1:]
    elif rel.startswith(root_path):
        rel = rel[len(root_path):].lstrip('/')
    return rel_upload_path(site_name, rel)
