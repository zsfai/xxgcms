# coding: utf-8
"""Shared file upload helpers."""
import random

import arrow
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

IMAGE_EXTENSIONS = frozenset({'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'})


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
