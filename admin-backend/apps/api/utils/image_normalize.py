# coding: utf-8
"""Normalize uploaded images: max 1200px edge, JPEG, <= 1MB."""
from io import BytesIO

from PIL import Image, ImageOps

MAX_EDGE = 1200
MAX_BYTES = 1 * 1024 * 1024
RAW_MAX_BYTES = 15 * 1024 * 1024
_QUALITY_STEPS = (85, 78, 70, 62, 54, 46, 40)


def normalize_image_bytes(raw, filename=''):  # noqa: ARG001 — filename reserved for callers
    if not raw:
        raise ValueError('图片内容为空')
    if len(raw) > RAW_MAX_BYTES:
        raise ValueError('原始图片不能超过 15MB')

    try:
        image = Image.open(BytesIO(raw))
        image = ImageOps.exif_transpose(image)
        image.load()
    except Exception as exc:
        raise ValueError('无法解析图片：%s' % exc) from exc

    if getattr(image, 'n_frames', 1) > 1:
        image.seek(0)

    if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
        rgba = image.convert('RGBA')
        background = Image.new('RGB', rgba.size, (255, 255, 255))
        background.paste(rgba, mask=rgba.split()[-1])
        image = background
    else:
        image = image.convert('RGB')

    image.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)

    last = None
    for quality in _QUALITY_STEPS:
        buf = BytesIO()
        image.save(buf, format='JPEG', quality=quality, optimize=True)
        last = buf.getvalue()
        if len(last) <= MAX_BYTES:
            return last, 'jpg'
    raise ValueError('压缩后仍超过 1MB，请换更小的图片')
