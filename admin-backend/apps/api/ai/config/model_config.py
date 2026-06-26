# coding: utf-8
"""Load AI provider/model configuration from lzcms DB（界面配置优先，环境变量备用）。"""
import json
import os
from typing import Any, Dict, Optional

from apps.api.ai.providers.base import ResolvedProvider
from apps.api.db.connection import xxgcms_connection

_CACHE: Dict[str, Any] = {'loaded': False, 'providers': {}, 'models': {}, 'settings': {}}

CAPABILITY_TO_SETTING = {
    'text_generation': 'default_text_provider',
    'image_generation': 'default_image_provider',
    'web_search': 'default_search_provider',
}

CAPABILITY_TO_ENV = {
    'text_generation': 'AI_DEFAULT_TEXT_PROVIDER',
    'image_generation': 'AI_DEFAULT_IMAGE_PROVIDER',
    'web_search': 'AI_DEFAULT_SEARCH_PROVIDER',
}

CAPABILITY_FALLBACK = {
    'text_generation': 'deepseek',
    'image_generation': 'qwen',
    'web_search': 'bocha',
}


def _parse_json(val):
    if val is None:
        return {}
    if isinstance(val, dict):
        return val
    try:
        return json.loads(val)
    except (TypeError, json.JSONDecodeError):
        return {}


def refresh_cache():
    _CACHE['loaded'] = False
    load_cache(force=True)


def load_cache(force=False):
    if _CACHE['loaded'] and not force:
        return
    providers = {}
    models_by_cap = {}
    settings = {}
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                'SELECT id, code, name, provider_type, base_url, api_key_env, api_key, enabled, extra_config '
                'FROM ai_provider WHERE enabled=%s',
                ('Y',),
            )
            for row in cursor.fetchall():
                providers[row['code']] = row
            cursor.execute(
                'SELECT m.*, p.code AS provider_code, p.base_url, p.api_key_env, p.api_key '
                'FROM ai_model m JOIN ai_provider p ON m.provider_id=p.id '
                'WHERE m.enabled=%s AND p.enabled=%s',
                ('Y', 'Y'),
            )
            for row in cursor.fetchall():
                cap = row['capability']
                models_by_cap.setdefault(cap, []).append(row)
            cursor.execute('SELECT config_key, config_value FROM ai_system_setting')
            for row in cursor.fetchall():
                settings[row['config_key']] = row['config_value']
    _CACHE['providers'] = providers
    _CACHE['models'] = models_by_cap
    _CACHE['settings'] = settings
    _CACHE['loaded'] = True


def _is_plausible_api_key(key: str) -> bool:
    key = (key or '').strip()
    if len(key) < 16:
        return False
    lowered = key.lower()
    if any(x in lowered for x in ('format string', 'traceback', 'authentication', 'invalid')):
        return False
    return True


def _resolve_api_key(prov: dict) -> str:
    db_key = (prov.get('api_key') or '').strip()
    if db_key and _is_plausible_api_key(db_key):
        return db_key
    env_name = (prov.get('api_key_env') or '').strip()
    if env_name:
        return os.environ.get(env_name, '').strip()
    return ''


def _default_provider_code(capability: str) -> str:
    setting_key = CAPABILITY_TO_SETTING.get(capability, '')
    if setting_key and _CACHE.get('settings', {}).get(setting_key):
        return _CACHE['settings'][setting_key]
    env_key = CAPABILITY_TO_ENV.get(capability, '')
    env_val = os.environ.get(env_key, '').strip() if env_key else ''
    return env_val or CAPABILITY_FALLBACK.get(capability, 'deepseek')


def resolve_provider(provider_code: Optional[str], capability: str) -> ResolvedProvider:
    load_cache()
    code = (provider_code or '').strip() or _default_provider_code(capability)
    prov = _CACHE['providers'].get(code)
    if not prov:
        raise ValueError('AI Provider 未配置或已禁用: %s' % code)
    api_key = _resolve_api_key(prov)
    if not api_key:
        raise ValueError(
            'Provider %s 未配置 API Key，请在「AI 配置」页面填写或设置环境变量 %s'
            % (code, prov.get('api_key_env') or ''),
        )
    models = _CACHE['models'].get(capability, [])
    model_row = None
    for m in models:
        if m['provider_code'] == code and m.get('is_default') == 'Y':
            model_row = m
            break
    if model_row is None:
        for m in models:
            if m['provider_code'] == code:
                model_row = m
                break
    default_model = model_row['model_id'] if model_row else ''
    params = _parse_json(model_row.get('params')) if model_row else {}
    extra = _parse_json(prov.get('extra_config'))
    base_url = (prov.get('base_url') or '').rstrip('/')
    return ResolvedProvider(
        code=code,
        base_url=base_url,
        api_key=api_key,
        default_model=default_model,
        params={**extra, **params},
    )


def list_models():
    load_cache()
    text_models = []
    image_models = []
    search_providers = []
    for cap, rows in _CACHE['models'].items():
        for row in rows:
            item = {
                'id': row['id'],
                'provider_code': row['provider_code'],
                'model_id': row['model_id'],
                'display_name': row.get('display_name') or row['model_id'],
                'capability': cap,
                'is_default': row.get('is_default') == 'Y',
            }
            if cap == 'text_generation':
                text_models.append(item)
            elif cap == 'image_generation':
                image_models.append(item)
    for code, prov in _CACHE['providers'].items():
        if prov.get('provider_type') == 'search':
            search_providers.append({
                'code': code,
                'name': prov.get('name') or code,
                'is_default': code == _default_provider_code('web_search'),
            })
    return {'text_models': text_models, 'image_models': image_models, 'search_providers': search_providers}


def list_providers():
    load_cache()
    result = []
    for code, prov in _CACHE['providers'].items():
        configured = bool(_resolve_api_key(prov))
        result.append({
            'code': code,
            'name': prov.get('name'),
            'provider_type': prov.get('provider_type'),
            'api_key_configured': configured,
        })
    return result
