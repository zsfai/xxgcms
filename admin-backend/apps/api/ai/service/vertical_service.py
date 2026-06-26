# coding: utf-8
"""垂类（vertical）配置 CRUD 与默认种子。"""
import json
import re

from apps.api.ai.mapper import ai_mapper
from apps.api.ai.service.template_service import seed_templates_if_empty

CODE_RE = re.compile(r'^[a-z][a-z0-9_]{0,30}$')


def _parse_search_queries(raw):
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    text = str(raw).strip()
    if not text:
        return []
    if text.startswith('['):
        try:
            data = json.loads(text)
            if isinstance(data, list):
                return [str(x).strip() for x in data if str(x).strip()]
        except json.JSONDecodeError:
            pass
    return [line.strip() for line in text.splitlines() if line.strip()]


def _serialize_vertical(row, include_prompts=True):
    if not row:
        return None
    item = dict(row)
    queries = _parse_search_queries(item.get('search_queries'))
    item['search_queries'] = queries
    item['enabled'] = item.get('enabled') == 'Y'
    if not include_prompts:
        for key in (
            'topic_system_prompt', 'topic_user_hint',
            'article_system_prompt', 'article_user_hint',
        ):
            item.pop(key, None)
    return item


def seed_verticals_if_empty():
    if ai_mapper.list_verticals():
        return
    defaults = [
        {
            'code': 'travel',
            'name': '旅游',
            'description': '旅游目的地、攻略、门票与出行实用内容',
            'topic_system_prompt': (
                '你是资深旅游内容策划编辑，熟悉国内旅游目的地、季节玩法、交通住宿与门票政策。'
                '根据联网检索摘要提炼选题建议。不得捏造检索中未出现的事实；'
                '不确定的价格、开放时间、政策须标注「待核实」。选题标题适合 SEO，角度清晰、可写性强。'
                '输出必须是合法 JSON，不要 markdown 代码块。'
            ),
            'topic_user_hint': '优先推荐有检索依据、对读者有决策价值的选题；避免空泛口号式标题。',
            'article_system_prompt': (
                '你是专业旅游攻略作者，擅长撰写实用、可落地的出行指南。结构清晰、信息密度高，'
                '含交通、门票、游玩顺序、避坑等可执行建议。不得捏造票价、开放时间、交通管制。'
                '时间敏感信息若无法核实须标注待核实。输出纯 JSON，不要 markdown。'
            ),
            'article_user_hint': '正文小节 3-5 个；image_hint 用英文描述场景，便于 AI 配图。',
            'search_queries': json.dumps([
                '{seed} 旅游攻略 {year}',
                '{seed} 最新 门票 政策',
                '{seed} 必去 景点 推荐',
                '{seed} 交通 住宿 攻略',
                '{seed} 最佳旅游时间',
            ], ensure_ascii=False),
            'default_template_code': 'travel_guide',
            'default_word_count': 800,
            'sort_num': 10,
            'enabled': True,
        },
        {
            'code': 'news',
            'name': '资讯',
            'description': '行业动态、政策解读与时事资讯',
            'topic_system_prompt': (
                '你是资深资讯编辑，擅长从检索结果中提炼有新闻价值、可深度解读的选题。'
                '不得捏造事实与数据；不确定的信息标注「待核实」。选题应具备时效性与可读性。'
                '输出必须是合法 JSON，不要 markdown 代码块。'
            ),
            'topic_user_hint': '关注近半年内有讨论度的议题；标题客观，避免标题党。',
            'article_system_prompt': (
                '你是资深资讯作者，客观准确、逻辑清楚。导语点明核心信息，正文分层展开，避免空话套话。'
                '不得捏造数据与引述。输出纯 JSON，不要 markdown。'
            ),
            'article_user_hint': '涉及政策、数据时若检索未证实，正文须写「待核实」或回避具体数字。',
            'search_queries': json.dumps([
                '{seed} 最新 动态 {year}',
                '{seed} 行业 新闻',
                '{seed} 政策 解读',
            ], ensure_ascii=False),
            'default_template_code': 'news_general',
            'default_word_count': 800,
            'sort_num': 20,
            'enabled': True,
        },
        {
            'code': 'general',
            'name': '通用',
            'description': '通用主题内容，适合多数站点',
            'topic_system_prompt': (
                '你是资深内容策划编辑，能根据种子词与检索摘要提炼多样化选题。'
                '不得捏造检索中未出现的事实；不确定信息标注「待核实」。选题互不重复、适合 SEO。'
                '输出必须是合法 JSON，不要 markdown 代码块。'
            ),
            'topic_user_hint': '兼顾入门指南、常见问题、对比选购等读者常搜需求。',
            'article_system_prompt': (
                '你是资深内容作者，表达清晰、信息有用。根据标题与背景写出完整文章，不得捏造数据。'
                '输出纯 JSON，不要 markdown。'
            ),
            'article_user_hint': '正文 3-5 小节；每节配图 hint 用英文描述画面。',
            'search_queries': json.dumps([
                '{seed} 介绍',
                '{seed} 攻略 {year}',
                '{seed} 常见问题',
            ], ensure_ascii=False),
            'default_template_code': 'news_general',
            'default_word_count': 800,
            'sort_num': 30,
            'enabled': True,
        },
    ]
    for item in defaults:
        ai_mapper.create_vertical(item)


def list_for_topic_page():
    seed_verticals_if_empty()
    rows = ai_mapper.list_verticals(enabled_only=True)
    return [_serialize_vertical(r, include_prompts=False) for r in rows]


def list_for_admin():
    seed_verticals_if_empty()
    seed_templates_if_empty()
    rows = ai_mapper.list_verticals(enabled_only=False)
    templates = ai_mapper.list_prompt_templates(enabled_only=True)
    return {
        'verticals': [_serialize_vertical(r) for r in rows],
        'templates': [dict(t) for t in templates],
    }


def get_vertical(code, enabled_only=False):
    seed_verticals_if_empty()
    row = ai_mapper.get_vertical_by_code(code, enabled_only=enabled_only)
    return _serialize_vertical(row)


def create_vertical(payload):
    code = (payload.get('code') or '').strip().lower()
    name = (payload.get('name') or '').strip()
    if not CODE_RE.match(code):
        raise ValueError('标识仅支持小写字母、数字、下划线，且以字母开头')
    if not name:
        raise ValueError('名称不能为空')
    if ai_mapper.get_vertical_by_code(code):
        raise ValueError('标识已存在')
    topic_sys = (payload.get('topic_system_prompt') or '').strip()
    article_sys = (payload.get('article_system_prompt') or '').strip()
    if not topic_sys or not article_sys:
        raise ValueError('选题与写稿 system 提示不能为空')
    queries = _parse_search_queries(payload.get('search_queries'))
    if not queries:
        raise ValueError('请至少配置一条联网检索词模板')
    fields = {
        'code': code,
        'name': name,
        'description': (payload.get('description') or '').strip() or None,
        'topic_system_prompt': topic_sys,
        'topic_user_hint': (payload.get('topic_user_hint') or '').strip() or None,
        'article_system_prompt': article_sys,
        'article_user_hint': (payload.get('article_user_hint') or '').strip() or None,
        'search_queries': json.dumps(queries, ensure_ascii=False),
        'default_template_code': (payload.get('default_template_code') or '').strip() or None,
        'default_word_count': payload.get('default_word_count', 800),
        'sort_num': payload.get('sort_num', 9999),
        'enabled': payload.get('enabled', True),
    }
    new_id = ai_mapper.create_vertical(fields)
    return _serialize_vertical(ai_mapper.get_vertical_by_id(new_id))


def update_vertical(vertical_id, payload):
    row = ai_mapper.get_vertical_by_id(vertical_id)
    if not row:
        raise ValueError('垂类不存在')
    fields = {}
    if 'name' in payload:
        name = (payload.get('name') or '').strip()
        if not name:
            raise ValueError('名称不能为空')
        fields['name'] = name
    if 'description' in payload:
        fields['description'] = (payload.get('description') or '').strip() or None
    if 'topic_system_prompt' in payload:
        val = (payload.get('topic_system_prompt') or '').strip()
        if not val:
            raise ValueError('选题 system 提示不能为空')
        fields['topic_system_prompt'] = val
    if 'topic_user_hint' in payload:
        fields['topic_user_hint'] = (payload.get('topic_user_hint') or '').strip() or None
    if 'article_system_prompt' in payload:
        val = (payload.get('article_system_prompt') or '').strip()
        if not val:
            raise ValueError('写稿 system 提示不能为空')
        fields['article_system_prompt'] = val
    if 'article_user_hint' in payload:
        fields['article_user_hint'] = (payload.get('article_user_hint') or '').strip() or None
    if 'search_queries' in payload:
        queries = _parse_search_queries(payload.get('search_queries'))
        if not queries:
            raise ValueError('请至少配置一条联网检索词模板')
        fields['search_queries'] = json.dumps(queries, ensure_ascii=False)
    if 'default_template_code' in payload:
        fields['default_template_code'] = (payload.get('default_template_code') or '').strip() or None
    if 'default_word_count' in payload:
        fields['default_word_count'] = payload.get('default_word_count')
    if 'sort_num' in payload:
        fields['sort_num'] = payload.get('sort_num')
    if 'enabled' in payload:
        fields['enabled'] = payload.get('enabled')
    ai_mapper.update_vertical(vertical_id, fields)
    return _serialize_vertical(ai_mapper.get_vertical_by_id(vertical_id))


def delete_vertical(vertical_id):
    row = ai_mapper.get_vertical_by_id(vertical_id)
    if not row:
        raise ValueError('垂类不存在')
    ai_mapper.delete_vertical(vertical_id)
    return True
