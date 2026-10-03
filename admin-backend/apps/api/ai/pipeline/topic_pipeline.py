# coding: utf-8
import json

from apps.api.ai.config import model_config
from apps.api.ai.mapper import ai_mapper
from apps.api.ai.prompts.topic_prompts import (
    DEFAULT_TOPIC_SYSTEM_PROMPT,
    build_topic_user_prompt,
)
from apps.api.ai.providers.base import TextGenerateRequest
from apps.api.ai.providers.registry import get_text_provider
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


def run_topic_suggest(site_name, seed_keyword, cate_id, suggest_count, user_name):
    seed = (seed_keyword or '').strip()
    if not seed:
        raise ValueError('种子词不能为空')
    suggest_count = min(int(suggest_count or 10), 15)
    text_config = model_config.resolve_provider(None, 'text_generation')
    session_id = ai_mapper.create_topic_session(
        site_name, seed, 'general', cate_id, suggest_count,
        'none',
        user_name,
    )
    context_text = (
        '请基于种子词提出对读者有实际帮助的选题；涉及具体政策/价格/时间请标注待核实。\n'
        '种子词：%s' % seed
    )
    cate_name = _get_cate_name(site_name, cate_id)
    system_prompt = DEFAULT_TOPIC_SYSTEM_PROMPT
    user_prompt = build_topic_user_prompt(
        seed,
        cate_name,
        suggest_count,
        context_text,
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
        t['refs'] = []
        enriched.append(t)
    ai_mapper.insert_suggestions(session_id, enriched)
    ai_mapper.update_topic_session(
        session_id,
        status='ready',
        search_degraded='N',
        text_model=text_config.default_model,
    )
    return ai_mapper.get_topic_session(session_id)
