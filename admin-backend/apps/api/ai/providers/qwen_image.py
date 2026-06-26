# coding: utf-8
"""通义万相 / DashScope 图像生成（wanx 旧版 + wan2.7 新版）。"""
import base64
import os
import time

import requests

from apps.api.ai.providers.base import (
    ImageGenerateRequest,
    ImageGenerateResult,
    ImageProvider,
    ResolvedProvider,
)
from apps.api.ai.providers.registry import register_image_provider

DEFAULT_IMAGE_BASE = 'https://dashscope.aliyuncs.com/api/v1'


def _resolve_image_base_url(config: ResolvedProvider) -> str:
    custom = (config.params.get('image_base_url') or '').strip()
    if custom:
        return custom.rstrip('/')
    env = os.environ.get('DASHSCOPE_IMAGE_BASE_URL', '').strip()
    if env:
        return env.rstrip('/')
    base = (config.base_url or '').strip().rstrip('/')
    if not base or 'compatible-mode' in base:
        return DEFAULT_IMAGE_BASE
    return base


def _is_wan27_model(model: str) -> bool:
    m = (model or '').lower()
    return m.startswith('wan2.7') or m.startswith('wan2-7')


class QwenImageProvider(ImageProvider):
    def generate(self, req: ImageGenerateRequest, config: ResolvedProvider) -> ImageGenerateResult:
        model = req.model_id or config.default_model or 'wanx2.1-t2i-turbo'
        base_url = _resolve_image_base_url(config)
        if _is_wan27_model(model):
            return self._generate_wan27(req, config, base_url, model)
        return self._generate_wanx(req, config, base_url, model)

    def _generate_wan27(self, req, config, base_url, model) -> ImageGenerateResult:
        url = '%s/services/aigc/multimodal-generation/generation' % base_url
        size = req.params.get('size') or config.params.get('size', '2K')
        headers = {
            'Authorization': 'Bearer %s' % config.api_key,
            'Content-Type': 'application/json',
        }
        body = {
            'model': model,
            'input': {
                'messages': [
                    {
                        'role': 'user',
                        'content': [{'text': req.prompt}],
                    },
                ],
            },
            'parameters': {
                'size': size,
                'n': 1,
                'watermark': False,
            },
        }
        resp = requests.post(url, json=body, headers=headers, timeout=120)
        if resp.status_code >= 400:
            raise RuntimeError('万相 API 错误: %s %s' % (resp.status_code, resp.text[:300]))
        data = resp.json()
        choices = (data.get('output') or {}).get('choices') or []
        if not choices:
            raise RuntimeError('万相 API 未返回结果: %s' % str(data)[:300])
        content = choices[0].get('message', {}).get('content') or []
        for item in content:
            if item.get('type') == 'image' and item.get('image'):
                return self._download(item['image'], data)
            if item.get('image'):
                return self._download(item['image'], data)
        raise RuntimeError('万相 API 结果中无图片 URL')

    def _generate_wanx(self, req, config, base_url, model) -> ImageGenerateResult:
        size = req.params.get('size') or config.params.get('size', '1280*720')
        url = '%s/services/aigc/text2image/image-synthesis' % base_url
        headers = {
            'Authorization': 'Bearer %s' % config.api_key,
            'Content-Type': 'application/json',
            'X-DashScope-Async': 'enable',
        }
        body = {
            'model': model,
            'input': {'prompt': req.prompt},
            'parameters': {'size': size, 'n': 1},
        }
        resp = requests.post(url, json=body, headers=headers, timeout=60)
        if resp.status_code >= 400:
            raise RuntimeError('万相 API 错误: %s %s' % (resp.status_code, resp.text[:300]))
        data = resp.json()
        task_id = data.get('output', {}).get('task_id')
        if not task_id:
            results = data.get('output', {}).get('results', [])
            if results:
                img_url = results[0].get('url')
                if img_url:
                    return self._download(img_url, data)
            raise RuntimeError('万相 API 未返回 task_id: %s' % str(data)[:300])
        task_url = '%s/tasks/%s' % (base_url, task_id)
        for _ in range(60):
            time.sleep(2)
            tr = requests.get(
                task_url,
                headers={'Authorization': 'Bearer %s' % config.api_key},
                timeout=30,
            )
            td = tr.json()
            status = td.get('output', {}).get('task_status') or td.get('task_status')
            if status == 'SUCCEEDED':
                results = td.get('output', {}).get('results', [])
                if not results:
                    raise RuntimeError('万相任务成功但无结果')
                img_url = results[0].get('url')
                if not img_url:
                    b64 = results[0].get('b64_image')
                    if b64:
                        return ImageGenerateResult(
                            image_bytes=base64.b64decode(b64),
                            mime_type='image/png',
                            raw_response=td,
                        )
                    raise RuntimeError('万相结果无 url')
                return self._download(img_url, td)
            if status in ('FAILED', 'CANCELED'):
                raise RuntimeError('万相任务失败: %s' % td)
        raise RuntimeError('万相任务超时')

    def _download(self, img_url: str, raw: dict) -> ImageGenerateResult:
        r = requests.get(img_url, timeout=60)
        if r.status_code >= 400:
            raise RuntimeError('下载生成图片失败: %s' % r.status_code)
        mime = r.headers.get('Content-Type', 'image/png').split(';')[0]
        return ImageGenerateResult(image_bytes=r.content, mime_type=mime, raw_response=raw)


register_image_provider('qwen', QwenImageProvider)
