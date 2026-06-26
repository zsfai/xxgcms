# coding: utf-8
from apps.api.ai.config import model_config
from apps.api.ai.mapper import ai_mapper
from apps.api.ai.pipeline.article_pipeline import run_article_generate
from apps.api.ai.service.batch_runner import start_job_async
from apps.api.service import article_service


def generate_single(site_name, title, cate_id, template_code, word_count, image_mode, user_name,
                    text_model_id=None, image_model_id=None):
    return run_article_generate(
        site_name, title, cate_id, template_code, word_count, image_mode,
        text_model_id=text_model_id, image_model_id=image_model_id,
    )


def batch_from_titles(site_name, titles, cate_id, template_code, word_count, image_mode, user_name):
    titles = [t.strip() for t in titles if (t or '').strip()]
    if not titles:
        raise ValueError('标题列表为空')
    if len(titles) > 10:
        raise ValueError('单次最多 10 条标题')
    job_id = ai_mapper.create_batch_job(
        site_name, None, cate_id, template_code, word_count, image_mode, len(titles), user_name,
    )
    for t in titles:
        ai_mapper.create_batch_item(job_id, t)
    start_job_async(job_id)
    return job_id


def get_batch_job(job_id):
    return ai_mapper.get_batch_job(job_id)


def regenerate_body(site_name, article_id):
    info = article_service.get_article_detail(site_name, article_id)
    if not info:
        raise ValueError('文章不存在')
    kws = article_service.get_article_kws(site_name, article_id)
    title = info.get('title', '')
    cate_id = info.get('cate_id', -1)
    result = run_article_generate(
        site_name, title, cate_id, 'news_general', 800, 'none',
    )
    article_service.add_or_update_article(
        site_name, article_id, cate_id, title, info.get('show_type', 1),
        result['content'], result['desc'], kws,
        info.get('pic_url', ''), info.get('slug_url', ''), publish=False,
    )
    return result


def list_models():
    return model_config.list_models()


def list_providers():
    return model_config.list_providers()


def refresh_config():
    model_config.refresh_cache()


def get_admin_config():
    from apps.api.ai.service.config_service import get_admin_config as _get
    return _get()


def update_provider_config(**kwargs):
    from apps.api.ai.service.config_service import update_provider
    return update_provider(**kwargs)


def update_model_config(**kwargs):
    from apps.api.ai.service.config_service import update_model
    return update_model(**kwargs)


def create_model_config(**kwargs):
    from apps.api.ai.service.config_service import create_model
    return create_model(**kwargs)


def update_default_providers(**kwargs):
    from apps.api.ai.service.config_service import update_defaults
    return update_defaults(**kwargs)
