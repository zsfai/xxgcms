# coding: utf-8
"""AI Provider / Model / 默认项 — 界面配置读写。"""
import json

from apps.api.ai.config import model_config
from apps.api.db.connection import xxgcms_connection

SETTING_KEYS = (
    'default_text_provider',
    'default_image_provider',
    'default_search_provider',
)

CAPABILITY_BY_PROVIDER_TYPE = {
    'text': 'text_generation',
    'image': 'image_generation',
    'search': 'web_search',
}


def _is_plausible_api_key(key: str) -> bool:
    """过滤误写入的错误信息或过短字符串。"""
    key = (key or '').strip()
    if len(key) < 16:
        return False
    lowered = key.lower()
    if any(x in lowered for x in ('format string', 'traceback', 'authentication', 'invalid')):
        return False
    return True


def _mask_key(key: str) -> str:
    if not key:
        return ''
    if len(key) <= 8:
        return '*' * len(key)
    return '%s...%s' % (key[:4], key[-4:])


def _parse_json(val):
    return model_config._parse_json(val)


def _get_setting(cursor, key, default=''):
    cursor.execute('SELECT config_value FROM ai_system_setting WHERE config_key=%s', (key,))
    row = cursor.fetchone()
    return row['config_value'] if row else default


def _set_setting(cursor, key, value):
    cursor.execute(
        'INSERT INTO ai_system_setting (config_key, config_value) VALUES (%s,%s) '
        'ON DUPLICATE KEY UPDATE config_value=%s',
        (key, value, value),
    )


def get_admin_config():
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                'SELECT id, code, name, provider_type, base_url, api_key_env, api_key, enabled, extra_config '
                'FROM ai_provider ORDER BY id ASC',
            )
            providers = []
            for row in cursor.fetchall():
                key = (row.get('api_key') or '').strip()
                if key and not _is_plausible_api_key(key):
                    key = ''
                if not key and row.get('api_key_env'):
                    import os
                    key = os.environ.get(row['api_key_env'] or '', '').strip()
                providers.append({
                    'id': row['id'],
                    'code': row['code'],
                    'name': row['name'],
                    'provider_type': row['provider_type'],
                    'base_url': row.get('base_url') or '',
                    'api_key_env': row.get('api_key_env') or '',
                    'api_key_masked': _mask_key(key),
                    'api_key_configured': bool(key),
                    'enabled': row.get('enabled') == 'Y',
                    'extra_config': _parse_json(row.get('extra_config')),
                })
            cursor.execute(
                'SELECT m.id, m.provider_id, m.model_id, m.display_name, m.capability, '
                'm.is_default, m.params, m.enabled, p.code AS provider_code '
                'FROM ai_model m JOIN ai_provider p ON m.provider_id=p.id ORDER BY m.id ASC',
            )
            models = []
            for row in cursor.fetchall():
                models.append({
                    'id': row['id'],
                    'provider_id': row['provider_id'],
                    'provider_code': row['provider_code'],
                    'model_id': row['model_id'],
                    'display_name': row.get('display_name') or row['model_id'],
                    'capability': row['capability'],
                    'is_default': row.get('is_default') == 'Y',
                    'params': _parse_json(row.get('params')),
                    'enabled': row.get('enabled') == 'Y',
                })
            defaults = {}
            for key in SETTING_KEYS:
                defaults[key] = _get_setting(cursor, key, '')
    # 未写入 DB 时回退种子/环境
    import os
    if not defaults.get('default_text_provider'):
        defaults['default_text_provider'] = os.environ.get('AI_DEFAULT_TEXT_PROVIDER', 'deepseek')
    if not defaults.get('default_image_provider'):
        defaults['default_image_provider'] = os.environ.get('AI_DEFAULT_IMAGE_PROVIDER', 'qwen')
    if not defaults.get('default_search_provider'):
        defaults['default_search_provider'] = os.environ.get('AI_DEFAULT_SEARCH_PROVIDER', 'bocha')
    return {'providers': providers, 'models': models, 'defaults': defaults}


def update_provider(provider_id, name=None, base_url=None, api_key=None, clear_api_key=False, enabled=None, extra_config=None):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT id FROM ai_provider WHERE id=%s', (provider_id,))
            if not cursor.fetchone():
                raise ValueError('Provider 不存在')
            updates = {}
            if name is not None:
                updates['name'] = name
            if base_url is not None:
                updates['base_url'] = base_url
            if enabled is not None:
                updates['enabled'] = 'Y' if enabled else 'N'
            if extra_config is not None:
                updates['extra_config'] = json.dumps(extra_config, ensure_ascii=False)
            if clear_api_key:
                updates['api_key'] = ''
            elif api_key is not None and api_key.strip():
                cleaned = api_key.strip()
                if not _is_plausible_api_key(cleaned):
                    raise ValueError('API Key 格式异常，请填写完整的 Key（勿粘贴错误提示文字）')
                updates['api_key'] = cleaned
            if not updates:
                return True
            cols = ', '.join(['`%s`=%s' % (k, '%s') for k in updates])
            cursor.execute(
                'UPDATE ai_provider SET ' + cols + ' WHERE id=%s',
                tuple(updates.values()) + (provider_id,),
            )
            conn.commit()
    model_config.refresh_cache()
    return True


def update_model(model_id, model_id_str=None, display_name=None, params=None, is_default=None, enabled=None):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                'SELECT m.id, m.capability FROM ai_model m WHERE m.id=%s',
                (model_id,),
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError('模型不存在')
            capability = row['capability']
            updates = {}
            if model_id_str is not None:
                updates['model_id'] = model_id_str
            if display_name is not None:
                updates['display_name'] = display_name
            if params is not None:
                updates['params'] = json.dumps(params, ensure_ascii=False)
            if enabled is not None:
                updates['enabled'] = 'Y' if enabled else 'N'
            if is_default is not None:
                updates['is_default'] = 'Y' if is_default else 'N'
            if updates:
                cols = ', '.join(['`%s`=%s' % (k, '%s') for k in updates])
                cursor.execute(
                    'UPDATE ai_model SET ' + cols + ' WHERE id=%s',
                    tuple(updates.values()) + (model_id,),
                )
            if is_default:
                cursor.execute(
                    'UPDATE ai_model SET is_default=%s WHERE capability=%s AND id<>%s',
                    ('N', capability, model_id),
                )
                cursor.execute('UPDATE ai_model SET is_default=%s WHERE id=%s', ('Y', model_id))
            conn.commit()
    model_config.refresh_cache()
    return True


def create_model(provider_id, model_id_str, display_name=None, is_default=False, enabled=True):
    if not model_id_str or not str(model_id_str).strip():
        raise ValueError('模型 ID 不能为空')
    model_id_str = str(model_id_str).strip()
    display_name = (display_name or model_id_str).strip()
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                'SELECT id, provider_type FROM ai_provider WHERE id=%s',
                (provider_id,),
            )
            prov = cursor.fetchone()
            if not prov:
                raise ValueError('Provider 不存在')
            capability = CAPABILITY_BY_PROVIDER_TYPE.get(prov['provider_type'])
            if not capability:
                raise ValueError('未知 Provider 类型')
            cursor.execute(
                'INSERT INTO ai_model (provider_id, model_id, display_name, capability, is_default, enabled) '
                'VALUES (%s,%s,%s,%s,%s,%s)',
                (
                    provider_id,
                    model_id_str,
                    display_name,
                    capability,
                    'Y' if is_default else 'N',
                    'Y' if enabled else 'N',
                ),
            )
            new_id = cursor.lastrowid
            if is_default:
                cursor.execute(
                    'UPDATE ai_model SET is_default=%s WHERE capability=%s AND id<>%s',
                    ('N', capability, new_id),
                )
                cursor.execute('UPDATE ai_model SET is_default=%s WHERE id=%s', ('Y', new_id))
            conn.commit()
    model_config.refresh_cache()
    return new_id


def update_defaults(default_text_provider=None, default_image_provider=None, default_search_provider=None):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            if default_text_provider:
                _set_setting(cursor, 'default_text_provider', default_text_provider)
            if default_image_provider:
                _set_setting(cursor, 'default_image_provider', default_image_provider)
            if default_search_provider:
                _set_setting(cursor, 'default_search_provider', default_search_provider)
            conn.commit()
    model_config.refresh_cache()
    return True


def seed_system_defaults_if_empty():
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) AS n FROM ai_system_setting')
            if cursor.fetchone()['n'] > 0:
                return
            _set_setting(cursor, 'default_text_provider', 'deepseek')
            _set_setting(cursor, 'default_image_provider', 'qwen')
            _set_setting(cursor, 'default_search_provider', 'bocha')
            conn.commit()
