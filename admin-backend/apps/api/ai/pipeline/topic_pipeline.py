# coding: utf-8
import json
import time

from apps.api.ai.config import model_config
from apps.api.ai.mapper import ai_mapper
from apps.api.ai.prompts.search_queries import expand_search_queries
from apps.api.ai.prompts.topic_prompts import build_topic_user_prompt, format_search_snippets
from apps.api.ai.providers.base import SearchRequest, TextGenerateRequest
from apps.api.ai.providers.registry import get_search_provider, get_text_provider
from apps.api.ai.service.vertical_service import get_vertical
from apps.api.db.connection import cms_x_connection


def _get_cate_name(site_name, cate_id):
    if not cate_id or cate_id <= 0:
        return ''
    try:
        with cms_x_connection(site_name) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT name FROM cate WHERE id=%s AND del_flag=%s', (cate_id, 'N'))
                row = cursor.fetchone()
                return row.get('name', '') if row else ''
    except Exception:
        return ''


def _parse_topics_json(content: str):
    data = json.loads(content)
    topics = data.get('topics', [])
    if not isinstance(topics, list):
        raise ValueError('topics 字段无效')
    return topics


def run_topic_suggest(site_name, seed_keyword, vertical, cate_id, suggest_count, search_provider_code, user_name):
    seed = (seed_keyword or '').strip()
    if not seed:
        raise ValueError('种子词不能为空')
    suggest_count = min(int(suggest_count or 10), 15)
    vertical = (vertical or 'general').strip()
    search_code = (search_provider_code or '').strip().lower()
    use_search = search_code not in ('', 'none', 'skip', 'off')
    text_config = model_config.resolve_provider(None, 'text_generation')
    vertical_row = get_vertical(vertical, enabled_only=True)
    if not vertical_row:
        vertical_row = get_vertical('general', enabled_only=True)
    if not vertical_row:
        raise ValueError('未配置可用垂类，请先在「垂类管理」中添加并启用')
    vertical_code = vertical_row.get('code') or vertical
    session_id = ai_mapper.create_topic_session(
        site_name, seed, vertical_code, cate_id, suggest_count,
        search_code if use_search else 'none',
        user_name,
    )
    search_degraded = not use_search
    snippets_text = ''
    search_items = []
    queries = expand_search_queries(seed, query_templates=vertical_row.get('search_queries'), vertical=vertical_code)
    if use_search:
        try:
            search_config = model_config.resolve_provider(search_provider_code, 'web_search')
            provider = get_search_provider(search_config.code)
            result = provider.search(
                SearchRequest(queries=queries, max_results_per_query=5),
                search_config,
            )
            search_items = result.items
            for q in queries:
                ai_mapper.insert_search_log(session_id, q, search_config.code, len(search_items), {'ok': True})
            snippets_text = format_search_snippets(search_items)
            search_degraded = False
        except Exception as exc:
            search_degraded = True
            snippets_text = (
                '（联网检索未成功，请基于种子词与常识给出选题，时效性内容标注待核实）\n种子词：%s'
            ) % seed
            ai_mapper.insert_search_log(
                session_id, seed, search_code, 0, {'error': str(exc)[:200]},
            )
    else:
        snippets_text = (
            '（未启用联网检索，请基于种子词与行业常识发散选题，涉及具体政策/票价/时间请标注待核实）\n'
            '种子词：%s' % seed
        )
    cate_name = _get_cate_name(site_name, cate_id)
    system_prompt = vertical_row.get('topic_system_prompt') or ''
    user_prompt = build_topic_user_prompt(
        seed,
        vertical_row.get('name') or vertical_code,
        cate_name,
        suggest_count,
        snippets_text,
        user_hint=vertical_row.get('topic_user_hint'),
    )
    text_provider = get_text_provider(text_config.code)
    req = TextGenerateRequest(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model_id=text_config.default_model,
    )
    text_result = text_provider.generate(req, text_config)
    try:
        topics = _parse_topics_json(text_result.content)
    except (json.JSONDecodeError, ValueError):
        req.system_prompt = system_prompt + ' 仅输出 JSON。'
        text_result = text_provider.generate(req, text_config)
        topics = _parse_topics_json(text_result.content)
    enriched = []
    for t in topics:
        refs = []
        for idx in t.get('ref_indexes', []) or []:
            if 1 <= idx <= len(search_items):
                item = search_items[idx - 1]
                refs.append({'title': item.title, 'url': item.url, 'snippet': item.snippet})
        t['refs'] = refs
        enriched.append(t)
    ai_mapper.insert_suggestions(session_id, enriched)
    ai_mapper.update_topic_session(
        session_id,
        status='ready',
        search_degraded='Y' if search_degraded else 'N',
        text_model=text_config.default_model,
    )
    return ai_mapper.get_topic_session(session_id)
