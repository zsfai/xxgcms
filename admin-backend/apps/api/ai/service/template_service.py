# coding: utf-8
"""文章写稿模板（prompt template）CRUD。"""
import re

from apps.api.ai.mapper import ai_mapper

CODE_RE = re.compile(r'^[a-z][a-z0-9_]{0,30}$')


def _serialize_template(row, include_prompt=True):
    if not row:
        return None
    item = dict(row)
    item['enabled'] = item.get('enabled') == 'Y'
    if not include_prompt:
        item.pop('system_prompt', None)
        item.pop('section_schema', None)
    return item


def list_for_topic():
    seed_templates_if_empty()
    rows = ai_mapper.list_prompt_templates_full(enabled_only=True)
    return [
        {
            'code': r['code'],
            'name': r['name'],
        }
        for r in rows
    ]


def list_for_admin():
    seed_templates_if_empty()
    rows = ai_mapper.list_prompt_templates_full(enabled_only=False)
    return [_serialize_template(r) for r in rows]


def create_template(payload):
    code = (payload.get('code') or '').strip().lower()
    name = (payload.get('name') or '').strip()
    if not CODE_RE.match(code):
        raise ValueError('标识仅支持小写字母、数字、下划线，且以字母开头')
    if not name:
        raise ValueError('名称不能为空')
    if ai_mapper.get_prompt_template_by_code(code):
        raise ValueError('标识已存在')
    system_prompt = (payload.get('system_prompt') or '').strip()
    if not system_prompt:
        raise ValueError('System 提示词不能为空')
    fields = {
        'code': code,
        'name': name,
        'system_prompt': system_prompt,
        'section_schema': (payload.get('section_schema') or '').strip() or None,
        'enabled': payload.get('enabled', True),
    }
    new_id = ai_mapper.create_prompt_template(fields)
    return _serialize_template(ai_mapper.get_prompt_template_by_id(new_id))


def update_template(template_id, payload):
    row = ai_mapper.get_prompt_template_by_id(template_id)
    if not row:
        raise ValueError('模板不存在')
    fields = {}
    if 'name' in payload:
        name = (payload.get('name') or '').strip()
        if not name:
            raise ValueError('名称不能为空')
        fields['name'] = name
    if 'system_prompt' in payload:
        val = (payload.get('system_prompt') or '').strip()
        if not val:
            raise ValueError('System 提示词不能为空')
        fields['system_prompt'] = val
    if 'section_schema' in payload:
        fields['section_schema'] = (payload.get('section_schema') or '').strip() or None
    if 'enabled' in payload:
        fields['enabled'] = payload.get('enabled')
    ai_mapper.update_prompt_template(template_id, fields)
    return _serialize_template(ai_mapper.get_prompt_template_by_id(template_id))


def delete_template(template_id):
    row = ai_mapper.get_prompt_template_by_id(template_id)
    if not row:
        raise ValueError('模板不存在')
    code = row['code']
    verticals = ai_mapper.list_verticals(enabled_only=False)
    used = [v['name'] for v in verticals if v.get('default_template_code') == code]
    if used:
        raise ValueError('该模板正在被垂类使用：%s' % '、'.join(used[:5]))
    ai_mapper.delete_prompt_template(template_id)
    return True


def seed_templates_if_empty():
    if ai_mapper.list_prompt_templates_full(enabled_only=False):
        return
    defaults = [
        {
            'code': 'news_general',
            'name': '通用资讯',
            'system_prompt': '你是资深资讯编辑，根据事实撰写客观报道。不得捏造数据。输出纯 JSON，不要 markdown。',
            'enabled': True,
        },
        {
            'code': 'industry_analysis',
            'name': '行业分析',
            'system_prompt': '你是行业分析师，撰写有深度的行业观察。不得捏造数据。输出纯 JSON，不要 markdown。',
            'enabled': True,
        },
        {
            'code': 'travel_guide',
            'name': '旅游攻略',
            'system_prompt': '你是资深旅游内容策划，撰写实用、准确的旅游攻略。不得捏造开放时间票价。输出纯 JSON，不要 markdown。',
            'enabled': True,
        },
    ]
    for item in defaults:
        ai_mapper.create_prompt_template(item)
