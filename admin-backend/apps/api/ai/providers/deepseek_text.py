# coding: utf-8
import json
import time

import requests

from apps.api.ai.providers.base import ResolvedProvider, TextGenerateRequest, TextGenerateResult, TextProvider
from apps.api.ai.providers.registry import register_text_provider


class DeepSeekTextProvider(TextProvider):
    def generate(self, req: TextGenerateRequest, config: ResolvedProvider) -> TextGenerateResult:
        model = req.model_id or config.default_model or 'deepseek-v4-pro'
        url = '%s/v1/chat/completions' % config.base_url
        body = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': req.system_prompt},
                {'role': 'user', 'content': req.user_prompt},
            ],
            'response_format': {'type': 'json_object'},
            'temperature': req.params.get('temperature', config.params.get('temperature', 0.7)),
            'max_tokens': req.params.get('max_tokens', config.params.get('max_tokens', 4096)),
        }
        headers = {
            'Authorization': 'Bearer %s' % config.api_key,
            'Content-Type': 'application/json',
        }
        for attempt in range(2):
            resp = requests.post(url, json=body, headers=headers, timeout=90)
            if resp.status_code >= 400:
                if attempt == 0:
                    time.sleep(1)
                    continue
                if resp.status_code == 401:
                    raise RuntimeError(
                        'DeepSeek API 认证失败：API Key 无效。请在「AI 配置」重新填写 DeepSeek Key 后保存。'
                    )
                raise RuntimeError('DeepSeek API 错误: %s %s' % (resp.status_code, resp.text[:300]))
            data = resp.json()
            content = data['choices'][0]['message']['content']
            usage = data.get('usage') or {}
            return TextGenerateResult(
                content=content,
                tokens_input=int(usage.get('prompt_tokens', 0)),
                tokens_output=int(usage.get('completion_tokens', 0)),
                raw_response=data,
            )
        raise RuntimeError('DeepSeek 调用失败')


register_text_provider('deepseek', DeepSeekTextProvider)
