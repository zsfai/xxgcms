# coding: utf-8
import json

import arrow

from apps.api.db.connection import xxgcms_connection


def _json_dumps(val):
    if val is None:
        return None
    return json.dumps(val, ensure_ascii=False)


def create_topic_session(site_name, seed, vertical, cate_id, suggest_count, search_provider, user_name):
    now = arrow.now().format('YYYY-MM-DD HH:mm:ss')
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                INSERT INTO ai_topic_session(
                  site_name, seed_keyword, vertical, cate_id, suggest_count,
                  status, search_provider, created_by, add_time
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ''',
                (site_name, seed, vertical, cate_id, suggest_count, 'searching', search_provider, user_name, now),
            )
            conn.commit()
            return cursor.lastrowid


def update_topic_session(session_id, **fields):
    allowed = ('status', 'search_degraded', 'text_model', 'update_time')
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return
    if 'update_time' not in updates:
        updates['update_time'] = arrow.now().format('YYYY-MM-DD HH:mm:ss')
    cols = ', '.join(['`%s`=%s' % (k, '%s') for k in updates])
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                'UPDATE ai_topic_session SET ' + cols + ' WHERE id=%s',
                tuple(updates.values()) + (session_id,),
            )
            conn.commit()


def insert_suggestions(session_id, topics):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            for idx, t in enumerate(topics):
                cursor.execute(
                    '''
                    INSERT INTO ai_topic_suggestion(
                      session_id, title, angle, timeliness, summary, ref_snippets, status, sort_num
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    ''',
                    (
                        session_id,
                        t.get('title', ''),
                        t.get('angle', ''),
                        t.get('timeliness', ''),
                        t.get('summary', ''),
                        _json_dumps(t.get('refs')),
                        'suggested',
                        idx,
                    ),
                )
            conn.commit()


def insert_search_log(session_id, query, provider, result_count, raw_preview):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                INSERT INTO ai_search_log(session_id, query, provider, result_count, raw_preview, add_time)
                VALUES (%s,%s,%s,%s,%s,%s)
                ''',
                (
                    session_id, query, provider, result_count,
                    _json_dumps(raw_preview),
                    arrow.now().format('YYYY-MM-DD HH:mm:ss'),
                ),
            )
            conn.commit()


def get_topic_session(session_id):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM ai_topic_session WHERE id=%s', (session_id,))
            session = cursor.fetchone()
            if not session:
                return None
            cursor.execute(
                'SELECT * FROM ai_topic_suggestion WHERE session_id=%s ORDER BY sort_num ASC, id ASC',
                (session_id,),
            )
            suggestions = cursor.fetchall()
            return {'session': session, 'suggestions': suggestions}


def list_topic_sessions(site_name, limit=10):
    limit = min(int(limit or 10), 20)
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                SELECT DISTINCT s.*
                FROM ai_topic_session s
                INNER JOIN ai_topic_suggestion g
                    ON g.session_id = s.id AND g.status = 'generated'
                WHERE s.site_name = %s
                ORDER BY s.id DESC
                LIMIT %s
                ''',
                (site_name, limit),
            )
            sessions = cursor.fetchall()
            result = []
            for session in sessions:
                cursor.execute(
                    '''
                    SELECT * FROM ai_topic_suggestion
                    WHERE session_id = %s AND status = 'generated'
                    ORDER BY sort_num ASC, id ASC
                    ''',
                    (session['id'],),
                )
                suggestions = cursor.fetchall()
                if suggestions:
                    result.append({'session': session, 'suggestions': suggestions})
            return result


def update_suggestions(updates):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            for item in updates:
                sid = item.get('id')
                if not sid:
                    continue
                fields = {}
                if 'title' in item:
                    fields['title'] = item['title']
                if 'status' in item:
                    fields['status'] = item['status']
                if not fields:
                    continue
                cols = ', '.join(['`%s`=%s' % (k, '%s') for k in fields])
                cursor.execute(
                    'UPDATE ai_topic_suggestion SET ' + cols + ' WHERE id=%s',
                    tuple(fields.values()) + (sid,),
                )
            conn.commit()


def create_batch_job(site_name, session_id, cate_id, template_code, word_count, image_mode, total, user_name):
    now = arrow.now().format('YYYY-MM-DD HH:mm:ss')
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                INSERT INTO ai_batch_job(
                  site_name, session_id, cate_id, template_code, word_count, image_mode,
                  status, total, done, failed, created_by, add_time
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,0,0,%s,%s)
                ''',
                (site_name, session_id, cate_id, template_code, word_count, image_mode, 'pending', total, user_name, now),
            )
            conn.commit()
            return cursor.lastrowid


def create_batch_item(job_id, title, suggestion_id=None):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO ai_batch_item(job_id, title, suggestion_id, status) VALUES (%s,%s,%s,%s)',
                (job_id, title, suggestion_id, 'pending'),
            )
            conn.commit()
            return cursor.lastrowid


def update_batch_job(job_id, **fields):
    allowed = ('status', 'done', 'failed', 'update_time')
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return
    if 'update_time' not in updates:
        updates['update_time'] = arrow.now().format('YYYY-MM-DD HH:mm:ss')
    cols = ', '.join(['`%s`=%s' % (k, '%s') for k in updates])
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                'UPDATE ai_batch_job SET ' + cols + ' WHERE id=%s',
                tuple(updates.values()) + (job_id,),
            )
            conn.commit()


def update_batch_item(item_id, **fields):
    allowed = ('status', 'article_id', 'error_message', 'log_id')
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return
    cols = ', '.join(['`%s`=%s' % (k, '%s') for k in updates])
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                'UPDATE ai_batch_item SET ' + cols + ' WHERE id=%s',
                tuple(updates.values()) + (item_id,),
            )
            conn.commit()


def get_batch_job(job_id):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM ai_batch_job WHERE id=%s', (job_id,))
            job = cursor.fetchone()
            if not job:
                return None
            cursor.execute('SELECT * FROM ai_batch_item WHERE job_id=%s ORDER BY id ASC', (job_id,))
            items = cursor.fetchall()
            return {'job': job, 'items': items}


def insert_generation_log(**fields):
    now = arrow.now().format('YYYY-MM-DD HH:mm:ss')
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                INSERT INTO ai_generation_log(
                  site_name, article_id, title, text_provider, text_model,
                  image_provider, image_model, search_provider,
                  tokens_input, tokens_output, image_count, status, error_message, duration_ms, add_time
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ''',
                (
                    fields.get('site_name'),
                    fields.get('article_id'),
                    fields.get('title'),
                    fields.get('text_provider'),
                    fields.get('text_model'),
                    fields.get('image_provider'),
                    fields.get('image_model'),
                    fields.get('search_provider'),
                    fields.get('tokens_input', 0),
                    fields.get('tokens_output', 0),
                    fields.get('image_count', 0),
                    fields.get('status'),
                    fields.get('error_message'),
                    fields.get('duration_ms', 0),
                    now,
                ),
            )
            conn.commit()
            return cursor.lastrowid


def mark_suggestion_generated(suggestion_id, article_id):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                'UPDATE ai_topic_suggestion SET status=%s, article_id=%s WHERE id=%s',
                ('generated', article_id, suggestion_id),
            )
            conn.commit()


def get_prompt_template(code):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                'SELECT * FROM ai_prompt_template WHERE code=%s AND enabled=%s',
                (code, 'Y'),
            )
            return cursor.fetchone()


def get_prompt_template_by_code(code):
    code = (code or '').strip()
    if not code:
        return None
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM ai_prompt_template WHERE code=%s', (code,))
            return cursor.fetchone()


def list_prompt_templates(enabled_only=True):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            if enabled_only:
                cursor.execute(
                    'SELECT code, name FROM ai_prompt_template WHERE enabled=%s ORDER BY id ASC',
                    ('Y',),
                )
            else:
                cursor.execute('SELECT code, name FROM ai_prompt_template ORDER BY id ASC')
            return cursor.fetchall()


def list_prompt_templates_full(enabled_only=False):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            if enabled_only:
                cursor.execute(
                    'SELECT * FROM ai_prompt_template WHERE enabled=%s ORDER BY id ASC',
                    ('Y',),
                )
            else:
                cursor.execute('SELECT * FROM ai_prompt_template ORDER BY id ASC')
            return cursor.fetchall()


def get_prompt_template_by_id(template_id):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM ai_prompt_template WHERE id=%s', (template_id,))
            return cursor.fetchone()


def create_prompt_template(fields):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                INSERT INTO ai_prompt_template(code, name, system_prompt, section_schema, enabled)
                VALUES (%s,%s,%s,%s,%s)
                ''',
                (
                    fields['code'],
                    fields['name'],
                    fields.get('system_prompt'),
                    fields.get('section_schema'),
                    'Y' if fields.get('enabled') else 'N',
                ),
            )
            conn.commit()
            return cursor.lastrowid


def update_prompt_template(template_id, fields):
    allowed = ('name', 'system_prompt', 'section_schema', 'enabled')
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return
    if 'enabled' in updates:
        updates['enabled'] = 'Y' if updates['enabled'] in (True, 'Y', 1, '1') else 'N'
    cols = ', '.join(['`%s`=%s' % (k, '%s') for k in updates])
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                'UPDATE ai_prompt_template SET ' + cols + ' WHERE id=%s',
                tuple(updates.values()) + (template_id,),
            )
            conn.commit()


def delete_prompt_template(template_id):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM ai_prompt_template WHERE id=%s', (template_id,))
            conn.commit()
            return cursor.rowcount


def list_verticals(enabled_only=False):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            if enabled_only:
                cursor.execute(
                    'SELECT * FROM ai_vertical WHERE enabled=%s ORDER BY sort_num ASC, id ASC',
                    ('Y',),
                )
            else:
                cursor.execute('SELECT * FROM ai_vertical ORDER BY sort_num ASC, id ASC')
            return cursor.fetchall()


def get_vertical_by_code(code, enabled_only=False):
    code = (code or '').strip()
    if not code:
        return None
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            if enabled_only:
                cursor.execute(
                    'SELECT * FROM ai_vertical WHERE code=%s AND enabled=%s',
                    (code, 'Y'),
                )
            else:
                cursor.execute('SELECT * FROM ai_vertical WHERE code=%s', (code,))
            return cursor.fetchone()


def get_vertical_by_id(vertical_id):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM ai_vertical WHERE id=%s', (vertical_id,))
            return cursor.fetchone()


def create_vertical(fields):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                INSERT INTO ai_vertical(
                  code, name, description, topic_system_prompt, topic_user_hint,
                  article_system_prompt, article_user_hint, search_queries,
                  default_template_code, default_word_count, sort_num, enabled
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ''',
                (
                    fields['code'],
                    fields['name'],
                    fields.get('description'),
                    fields['topic_system_prompt'],
                    fields.get('topic_user_hint'),
                    fields['article_system_prompt'],
                    fields.get('article_user_hint'),
                    fields['search_queries'],
                    fields.get('default_template_code'),
                    int(fields.get('default_word_count') or 800),
                    int(fields.get('sort_num') or 9999),
                    'Y' if fields.get('enabled') else 'N',
                ),
            )
            conn.commit()
            return cursor.lastrowid


def delete_vertical(vertical_id):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM ai_vertical WHERE id=%s', (vertical_id,))
            conn.commit()
            return cursor.rowcount


def update_vertical(vertical_id, fields):
    allowed = (
        'name', 'description', 'topic_system_prompt', 'topic_user_hint',
        'article_system_prompt', 'article_user_hint', 'search_queries',
        'default_template_code', 'default_word_count', 'sort_num', 'enabled',
    )
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return
    if 'enabled' in updates:
        updates['enabled'] = 'Y' if updates['enabled'] in (True, 'Y', 1, '1') else 'N'
    if 'default_word_count' in updates:
        updates['default_word_count'] = int(updates['default_word_count'] or 800)
    if 'sort_num' in updates:
        updates['sort_num'] = int(updates['sort_num'] or 9999)
    cols = ', '.join(['`%s`=%s' % (k, '%s') for k in updates])
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                'UPDATE ai_vertical SET ' + cols + ' WHERE id=%s',
                tuple(updates.values()) + (vertical_id,),
            )
            conn.commit()
