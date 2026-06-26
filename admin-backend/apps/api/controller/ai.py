# coding: utf-8
from django.views.decorators.csrf import csrf_exempt

from apps.api.ai.service import ai_service, topic_service
from apps.api.ai.service import vertical_service, template_service
from apps.api.utils.perm_wrapper import perm
from apps.api.utils.public import log_error
from apps.api.utils.response import api_error, api_success, parse_json


def _serialize_session(data):
    if not data:
        return None
    session = dict(data['session'])
    suggestions = []
    for s in data.get('suggestions', []):
        item = dict(s)
        if item.get('ref_snippets') and isinstance(item['ref_snippets'], str):
            import json
            try:
                item['refs'] = json.loads(item['ref_snippets'])
            except json.JSONDecodeError:
                item['refs'] = []
        else:
            item['refs'] = item.get('ref_snippets') or []
        suggestions.append(item)
    out = {'session': session, 'suggestions': suggestions}
    if data.get('job'):
        out['job'] = dict(data['job'])
        out['items'] = [dict(i) for i in data.get('items', [])]
    return out


def _serialize_session_list(entries):
    return [_serialize_session(entry) for entry in entries]


@csrf_exempt
@perm(code=None)
def topic_suggest(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        data = topic_service.suggest_topics(
            domain,
            req.get('seed_keyword', ''),
            req.get('vertical', 'general'),
            req.get('cate_id'),
            req.get('suggest_count', 10),
            req.get('search_provider'),
            request.xxgcms_user,
        )
        return api_success(data=_serialize_session(data))
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def topic_update(request):
    try:
        req = parse_json(request)
        topic_service.update_topic_suggestions(req.get('session_id'), req.get('updates', []))
        data = topic_service.get_session(req.get('session_id'))
        return api_success(data=_serialize_session(data))
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def topic_confirm_generate(request):
    try:
        req = parse_json(request)
        job_id = topic_service.confirm_and_generate(
            req.get('session_id'),
            req.get('suggestion_ids', []),
            req.get('template_code', 'news_general'),
            req.get('word_count', 800),
            req.get('image_mode', 'ai'),
            request.xxgcms_user,
        )
        return api_success(data={'job_id': job_id, 'session_id': req.get('session_id')})
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def topic_session(request):
    try:
        req = parse_json(request) if request.body else {}
        session_id = req.get('session_id') or request.GET.get('session_id')
        data = topic_service.get_session(int(session_id))
        return api_success(data=_serialize_session(data))
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def topic_sessions(request):
    try:
        req = parse_json(request) if request.body else {}
        domain = req.get('domain', '')
        limit = req.get('limit', 10)
        data = topic_service.list_recent_sessions(domain, limit)
        return api_success(data=_serialize_session_list(data))
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def verticals_for_topic(request):
    try:
        return api_success(data=vertical_service.list_for_topic_page())
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def verticals_admin(request):
    try:
        return api_success(data=vertical_service.list_for_admin())
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def create_vertical(request):
    try:
        req = parse_json(request)
        data = vertical_service.create_vertical(req)
        return api_success(data=data, ret=True)
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def update_vertical(request):
    try:
        req = parse_json(request)
        vertical_id = int(req.get('id'))
        data = vertical_service.update_vertical(vertical_id, req)
        return api_success(data=data, ret=True)
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def delete_vertical(request):
    try:
        req = parse_json(request)
        vertical_id = int(req.get('id'))
        vertical_service.delete_vertical(vertical_id)
        return api_success(ret=True)
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def templates_for_topic(request):
    try:
        return api_success(data=template_service.list_for_topic())
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def templates_admin(request):
    try:
        return api_success(data=template_service.list_for_admin())
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def create_template(request):
    try:
        req = parse_json(request)
        data = template_service.create_template(req)
        return api_success(data=data, ret=True)
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def update_template(request):
    try:
        req = parse_json(request)
        template_id = int(req.get('id'))
        data = template_service.update_template(template_id, req)
        return api_success(data=data, ret=True)
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def delete_template(request):
    try:
        req = parse_json(request)
        template_id = int(req.get('id'))
        template_service.delete_template(template_id)
        return api_success(ret=True)
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def generate_article(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        data = ai_service.generate_single(
            domain,
            req.get('title', ''),
            req.get('cate_id'),
            req.get('template_code', 'news_general'),
            req.get('word_count', 800),
            req.get('image_mode', 'ai'),
            request.xxgcms_user,
            req.get('text_model_id'),
            req.get('image_model_id'),
        )
        return api_success(data=data)
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def batch_generate(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        job_id = ai_service.batch_from_titles(
            domain,
            req.get('titles', []),
            req.get('cate_id'),
            req.get('template_code', 'news_general'),
            req.get('word_count', 800),
            req.get('image_mode', 'ai'),
            request.xxgcms_user,
        )
        return api_success(data={'job_id': job_id})
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def batch_job(request):
    try:
        req = parse_json(request) if request.body else {}
        job_id = req.get('job_id') or request.GET.get('job_id')
        data = ai_service.get_batch_job(int(job_id))
        if not data:
            return api_error('任务不存在')
        return api_success(data={
            'job': dict(data['job']),
            'items': [dict(i) for i in data['items']],
        })
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def regenerate_body(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        data = ai_service.regenerate_body(domain, req.get('article_id'))
        return api_success(data=data)
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def ai_models(request):
    try:
        return api_success(data=ai_service.list_models())
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def ai_providers(request):
    try:
        return api_success(data=ai_service.list_providers())
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def refresh_config(request):
    try:
        ai_service.refresh_config()
        return api_success(ret=True)
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def config_settings(request):
    try:
        from apps.api.ai.service.config_service import seed_system_defaults_if_empty
        seed_system_defaults_if_empty()
        return api_success(data=ai_service.get_admin_config())
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def update_provider_config(request):
    try:
        req = parse_json(request)
        ai_service.update_provider_config(
            provider_id=req.get('id'),
            name=req.get('name'),
            base_url=req.get('base_url'),
            api_key=req.get('api_key'),
            clear_api_key=req.get('clear_api_key') in (True, 1, '1', 'true'),
            enabled=req.get('enabled'),
            extra_config=req.get('extra_config'),
        )
        return api_success(ret=True, data=ai_service.get_admin_config())
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def update_model_config(request):
    try:
        req = parse_json(request)
        ai_service.update_model_config(
            model_id=req.get('id'),
            model_id_str=req.get('model_id'),
            display_name=req.get('display_name'),
            params=req.get('params'),
            is_default=req.get('is_default'),
            enabled=req.get('enabled'),
        )
        return api_success(ret=True, data=ai_service.get_admin_config())
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def create_model_config(request):
    try:
        req = parse_json(request)
        new_id = ai_service.create_model_config(
            provider_id=req.get('provider_id'),
            model_id_str=req.get('model_id'),
            display_name=req.get('display_name'),
            is_default=req.get('is_default') in (True, 1, '1', 'true'),
            enabled=req.get('enabled') not in (False, 0, '0', 'false'),
        )
        return api_success(ret=True, data=ai_service.get_admin_config(), id=new_id)
    except Exception as exc:
        return api_error(str(exc))


@csrf_exempt
@perm(code=None)
def update_default_providers(request):
    try:
        req = parse_json(request)
        ai_service.update_default_providers(
            default_text_provider=req.get('default_text_provider'),
            default_image_provider=req.get('default_image_provider'),
            default_search_provider=req.get('default_search_provider'),
        )
        return api_success(ret=True, data=ai_service.get_admin_config())
    except Exception as exc:
        return api_error(str(exc))
