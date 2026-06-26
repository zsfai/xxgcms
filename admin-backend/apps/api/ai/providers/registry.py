# coding: utf-8
from typing import Dict, Type

from apps.api.ai.providers.base import ImageProvider, SearchProvider, TextProvider

TEXT_PROVIDERS: Dict[str, Type[TextProvider]] = {}
IMAGE_PROVIDERS: Dict[str, Type[ImageProvider]] = {}
SEARCH_PROVIDERS: Dict[str, Type[SearchProvider]] = {}


def register_text_provider(code: str, cls: Type[TextProvider]):
    TEXT_PROVIDERS[code] = cls


def register_image_provider(code: str, cls: Type[ImageProvider]):
    IMAGE_PROVIDERS[code] = cls


def register_search_provider(code: str, cls: Type[SearchProvider]):
    SEARCH_PROVIDERS[code] = cls


def get_text_provider(code: str) -> TextProvider:
    if code not in TEXT_PROVIDERS:
        raise ValueError('未注册的文本 Provider: %s' % code)
    return TEXT_PROVIDERS[code]()


def get_image_provider(code: str) -> ImageProvider:
    if code not in IMAGE_PROVIDERS:
        raise ValueError('未注册的图像 Provider: %s' % code)
    return IMAGE_PROVIDERS[code]()


def get_search_provider(code: str) -> SearchProvider:
    if code not in SEARCH_PROVIDERS:
        raise ValueError('未注册的检索 Provider: %s' % code)
    return SEARCH_PROVIDERS[code]()
