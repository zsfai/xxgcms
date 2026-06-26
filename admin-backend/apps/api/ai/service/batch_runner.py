# coding: utf-8
import threading

from apps.api.ai.mapper import ai_mapper
from apps.api.ai.pipeline.article_pipeline import run_article_generate


def run_job(job_id):
    data = ai_mapper.get_batch_job(job_id)
    if not data:
        return
    job = data['job']
    items = data['items']
    ai_mapper.update_batch_job(job_id, status='running')
    done = 0
    failed = 0
    for item in items:
        ai_mapper.update_batch_item(item['id'], status='running')
        try:
            topic_context = None
            suggestion_id = item.get('suggestion_id')
            vertical_code = None
            if suggestion_id or job.get('session_id'):
                sess = ai_mapper.get_topic_session(job.get('session_id'))
                if sess and sess.get('session'):
                    vertical_code = sess['session'].get('vertical')
                if sess and suggestion_id:
                    for s in sess.get('suggestions', []):
                        if s['id'] == suggestion_id:
                            topic_context = s.get('summary') or ''
                            break
            result = run_article_generate(
                job['site_name'],
                item['title'],
                job.get('cate_id'),
                job.get('template_code') or 'news_general',
                job.get('word_count') or 800,
                job.get('image_mode') or 'ai',
                topic_context=topic_context,
                vertical_code=vertical_code,
            )
            ai_mapper.update_batch_item(
                item['id'],
                status='success',
                article_id=result.get('article_id'),
                log_id=result.get('log_id'),
            )
            if suggestion_id and result.get('article_id'):
                ai_mapper.mark_suggestion_generated(suggestion_id, result['article_id'])
            done += 1
        except Exception as exc:
            ai_mapper.update_batch_item(item['id'], status='failed', error_message=str(exc)[:500])
            failed += 1
        ai_mapper.update_batch_job(job_id, done=done, failed=failed)
    status = 'done' if failed == 0 else ('partial' if done > 0 else 'failed')
    ai_mapper.update_batch_job(job_id, status=status)
    if job.get('session_id'):
        ai_mapper.update_topic_session(job['session_id'], status='done')


def start_job_async(job_id):
    thread = threading.Thread(target=run_job, args=(job_id,), daemon=True)
    thread.start()
