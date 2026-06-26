# coding: utf-8
import json
import time

from apps.api.ai.config import model_config
from apps.api.ai.mapper import ai_mapper
from apps.api.ai.prompts.topic_prompts import build_article_system_prompt, build_article_user_prompt
from apps.api.ai.providers.base import ImageGenerateRequest, TextGenerateRequest
from apps.api.ai.providers.registry import get_image_provider, get_text_provider
from apps.api.ai.utils.media_save import save_ai_image, to_media_url
from apps.api.db.connection import cms_x_connection
from apps.api.service import article_service, slugurl_service

MAX_SECTION_IMAGES = 4


def _escape_html_attr(text: str) -> str:
    return (
        (text or '')
        .replace('&', '&amp;')
        .replace('"', '&quot;')
        .replace('<', '&lt;')
    )


def _assemble_html(site_name, sections, section_images=None):
    section_images = section_images or []
    parts = []
    for idx, sec in enumerate(sections or []):
        if not isinstance(sec, dict):
            continue
        heading = (sec.get('heading') or '').strip()
        body = (sec.get('body') or '').strip()
        img_url = section_images[idx] if idx < len(section_images) else None
        if heading:
            parts.append('<h2>%s</h2>' % heading)
        if img_url:
            alt = _escape_html_attr(heading or sec.get('image_hint') or '')
            media_src = to_media_url(site_name, img_url)
            parts.append(
                '<p style="text-align:center">'
                '<img src="%s" alt="%s" style="max-width:100%%;height:auto;" />'
                '</p>' % (media_src, alt)
            )
        if body:
            parts.append('<p>%s</p>' % body)
    return '\n'.join(parts) if parts else '<p></p>'


def _build_image_prompt(title: str, hint: str) -> str:
    hint = (hint or '').strip()
    if hint:
        return '%s，%s，高清摄影，无文字水印' % (title, hint)
    return '%s，高清摄影，无文字水印' % title


def _generate_section_images(site_name, title, sections, image_config, image_model, max_images=MAX_SECTION_IMAGES):
    img_provider = get_image_provider(image_config.code)
    urls = [None] * len(sections)
    errors = []
    count = 0
    for idx, sec in enumerate(sections[:max_images]):
        if not isinstance(sec, dict):
            continue
        hint = sec.get('image_hint') or sec.get('heading') or ''
        prompt = _build_image_prompt(title, hint)
        try:
            img_result = img_provider.generate(
                ImageGenerateRequest(prompt=prompt, model_id=image_model),
                image_config,
            )
            ext = 'png' if 'png' in img_result.mime_type else 'jpg'
            urls[idx] = save_ai_image(site_name, img_result.image_bytes, ext)
            count += 1
        except Exception as exc:
            errors.append(str(exc)[:120])
    return urls, count, errors


def _get_cate_name(site_name, cate_id):
    if not cate_id or cate_id <= 0:
        return ''
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT name FROM cate WHERE id=%s', (cate_id,))
            row = cursor.fetchone()
            return row.get('name', '') if row else ''


def _get_ref_titles(site_name, cate_id, limit=5):
    titles = []
    try:
        with cms_x_connection(site_name) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    'SELECT title FROM article WHERE cate_id=%s AND del_flag=%s AND pub_status=%s '
                    'ORDER BY pub_time DESC LIMIT %s',
                    (cate_id, 'N', 'Y', limit),
                )
                for row in cursor.fetchall():
                    titles.append(row.get('title', ''))
    except Exception:
        pass
    return titles


def _resolve_slug(site_name, title, suggested):
    slug = (suggested or '').strip()
    if slug:
        return slug
    try:
        return slugurl_service.generate_article_slug_url_by_title(site_name, title)
    except Exception:
        return ''


def _get_default_pic(site_name):
    try:
        conf = article_service.get_site_conf(site_name)
        if conf:
            return conf.get('defaul_pic_url', '') or ''
    except Exception:
        pass
    return ''


def run_article_generate(
    site_name,
    title,
    cate_id,
    template_code='news_general',
    word_count=800,
    image_mode='ai',
    topic_context=None,
    text_model_id=None,
    image_model_id=None,
    vertical_code=None,
):
    start_ms = int(time.time() * 1000)
    title = (title or '').strip()
    if not title:
        raise ValueError('标题不能为空')
    cate_id = int(cate_id or -1)
    template = ai_mapper.get_prompt_template(template_code) or {}
    template_name = template.get('name', template_code)
    vertical = None
    if vertical_code:
        from apps.api.ai.service.vertical_service import get_vertical
        vertical = get_vertical(vertical_code, enabled_only=False)
    if vertical and vertical.get('article_system_prompt'):
        system_prompt = vertical['article_system_prompt']
        article_user_hint = vertical.get('article_user_hint')
    else:
        if template.get('system_prompt'):
            system_prompt = template['system_prompt']
        else:
            system_prompt = build_article_system_prompt(template_code)
        article_user_hint = None
    text_config = model_config.resolve_provider(None, 'text_generation')
    if text_model_id:
        pass
    cate_name = _get_cate_name(site_name, cate_id)
    ref_titles = _get_ref_titles(site_name, cate_id)
    user_prompt = build_article_user_prompt(
        title, cate_name, template_name, int(word_count or 800), ref_titles, topic_context,
        user_hint=article_user_hint,
    )
    text_provider = get_text_provider(text_config.code)
    text_result = text_provider.generate(
        TextGenerateRequest(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_id=text_model_id or text_config.default_model,
        ),
        text_config,
    )
    data = json.loads(text_result.content)
    sections = data.get('sections') or []
    desc = (data.get('desc') or '')[:200]
    kws = data.get('kws') or []
    if not isinstance(kws, list):
        kws = []
    slug_url = _resolve_slug(site_name, title, data.get('suggested_slug'))
    pic_url = ''
    image_count = 0
    image_provider_code = None
    image_model = None
    image_error = None
    section_images = [None] * len(sections)
    if image_mode == 'ai':
        try:
            image_config = model_config.resolve_provider(None, 'image_generation')
            image_provider_code = image_config.code
            image_model = image_model_id or image_config.default_model
            section_images, image_count, img_errors = _generate_section_images(
                site_name, title, sections, image_config, image_model,
            )
            if section_images and section_images[0]:
                pic_url = section_images[0]
            else:
                pic_url = _get_default_pic(site_name)
            if img_errors:
                image_error = '; '.join(img_errors)[:200]
        except Exception as exc:
            image_error = str(exc)[:200]
            pic_url = _get_default_pic(site_name)
    elif image_mode == 'default':
        pic_url = _get_default_pic(site_name)
    content = _assemble_html(site_name, sections, section_images)
    article_id = article_service.add_or_update_article(
        site_name, -1, cate_id, title, 1, content, desc, kws, pic_url, slug_url, publish=False,
    )
    if article_id:
        with cms_x_connection(site_name) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    'UPDATE article SET ai_generated=%s WHERE id=%s',
                    ('Y', article_id),
                )
                conn.commit()
    duration_ms = int(time.time() * 1000) - start_ms
    log_id = ai_mapper.insert_generation_log(
        site_name=site_name,
        article_id=article_id,
        title=title,
        text_provider=text_config.code,
        text_model=text_config.default_model,
        image_provider=image_provider_code,
        image_model=image_model,
        tokens_input=text_result.tokens_input,
        tokens_output=text_result.tokens_output,
        image_count=image_count,
        status='success' if article_id else 'failed',
        error_message=image_error,
        duration_ms=duration_ms,
    )
    return {
        'article_id': article_id,
        'title': title,
        'content': content,
        'desc': desc,
        'kws': kws,
        'slug_url': slug_url,
        'pic_url': pic_url,
        'log_id': log_id,
    }
