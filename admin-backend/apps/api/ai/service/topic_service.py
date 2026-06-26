# coding: utf-8
from apps.api.ai.mapper import ai_mapper
from apps.api.ai.pipeline.topic_pipeline import run_topic_suggest
from apps.api.ai.service.batch_runner import start_job_async
from apps.api.db.connection import xxgcms_connection


def suggest_topics(site_name, seed_keyword, vertical, cate_id, suggest_count, search_provider, user_name):
    return run_topic_suggest(
        site_name, seed_keyword, vertical, cate_id, suggest_count, search_provider, user_name,
    )


def update_topic_suggestions(session_id, updates):
    ai_mapper.update_suggestions(updates)


def confirm_and_generate(session_id, suggestion_ids, template_code, word_count, image_mode, user_name):
    data = ai_mapper.get_topic_session(session_id)
    if not data:
        raise ValueError('选题会话不存在')
    session = data['session']
    if len(suggestion_ids) > 10:
        raise ValueError('单次最多确认 10 条选题')
    id_set = set(suggestion_ids)
    selected = [s for s in data['suggestions'] if s['id'] in id_set]
    if not selected:
        raise ValueError('请至少选择一条选题')
    job_id = ai_mapper.create_batch_job(
        session['site_name'],
        session_id,
        session.get('cate_id'),
        template_code,
        word_count,
        image_mode,
        len(selected),
        user_name,
    )
    for s in selected:
        ai_mapper.create_batch_item(job_id, s['title'], s['id'])
        ai_mapper.update_suggestions([{'id': s['id'], 'status': 'selected'}])
    ai_mapper.update_topic_session(session_id, status='generating')
    start_job_async(job_id)
    return job_id


def get_session(session_id):
    data = ai_mapper.get_topic_session(session_id)
    if not data:
        return None
    job_row = None
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                'SELECT * FROM ai_batch_job WHERE session_id=%s ORDER BY id DESC LIMIT 1',
                (session_id,),
            )
            job_row = cursor.fetchone()
    result = {
        'session': data['session'],
        'suggestions': data['suggestions'],
    }
    if job_row:
        batch = ai_mapper.get_batch_job(job_row['id'])
        result['job'] = batch.get('job')
        result['items'] = batch.get('items')
    return result


def list_recent_sessions(site_name, limit=10):
    return ai_mapper.list_topic_sessions(site_name, limit)
