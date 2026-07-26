# coding: utf-8
"""Shared file upload helpers."""
import random

import arrow
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

IMAGE_EXTENSIONS = frozenset({'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'})

MEDIA_IMAGE_EXTENSIONS = frozenset({'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp'})
MEDIA_VIDEO_EXTENSIONS = frozenset({'mp4', 'webm', 'mov', 'avi', 'mkv', 'm4v'})
MEDIA_DOCUMENT_EXTENSIONS = frozenset({
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'md', 'csv',
})
MEDIA_OTHER_EXTENSIONS = frozenset({'zip', 'rar', '7z', 'tar', 'gz'})
MEDIA_ALLOWED_EXTENSIONS = (
    MEDIA_IMAGE_EXTENSIONS
    | MEDIA_VIDEO_EXTENSIONS
    | MEDIA_DOCUMENT_EXTENSIONS
    | MEDIA_OTHER_EXTENSIONS
)
MEDIA_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB，与 nginx client_max_body_size 对齐


def save_upload(file, subdir, ext_name):
    timestamp = int(arrow.now().timestamp())
    name = f'{timestamp}_{random.random():.8f}'.replace('.', '')
    path = f'upload/{subdir}/{name}.{ext_name}'
    default_storage.save(path, ContentFile(file.read()))
    return path


def validate_image_ext(ext_name):
    ext = ext_name.lower()
    if ext not in IMAGE_EXTENSIONS:
        raise ValueError('上传的文件不合法')
    return ext


def classify_file_type(ext_name):
    """按扩展名归类：image / document / video / other。"""
    ext = (ext_name or '').lower().lstrip('.')
    if ext in MEDIA_IMAGE_EXTENSIONS:
        return 'image'
    if ext in MEDIA_VIDEO_EXTENSIONS:
        return 'video'
    if ext in MEDIA_DOCUMENT_EXTENSIONS:
        return 'document'
    if ext in MEDIA_OTHER_EXTENSIONS:
        return 'other'
    raise ValueError('上传的文件不合法')


def validate_media_ext(ext_name):
    ext = (ext_name or '').lower().lstrip('.')
    if ext not in MEDIA_ALLOWED_EXTENSIONS:
        raise ValueError('上传的文件不合法')
    return ext
