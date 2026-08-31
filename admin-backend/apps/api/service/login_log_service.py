# coding: utf-8
import os
import re

from django.conf import settings

from apps.api.db.connection import xxgcms_connection
from apps.api.sql_mapper.login_log_mapper import LoginLogMapper
from apps.api.utils.public import log_error


def add_login_log(user_name, action, ip='', user_agent='', message=''):
    name = (user_name or '')[:64]
    act = (action or '')[:32]
    ip_val = (ip or '')[:64]
    ua = (user_agent or '')[:512]
    msg = (message or '')[:255]
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                LoginLogMapper.insert_log(),
                (name, act, ip_val, ua, msg or None),
            )
            conn.commit()


def safe_add_login_log(user_name, action, ip='', user_agent='', message=''):
    try:
        add_login_log(user_name, action, ip=ip, user_agent=user_agent, message=message)
    except Exception as exc:
        log_error(f'写入登录日志失败: {exc}')


def get_login_log_list(
    start_page,
    page_size,
    user_name='',
    action='',
    start_time='',
    end_time='',
):
    conditions = []
    params = []
    name = (user_name or '').strip()
    if name:
        conditions.append('user_name LIKE %s')
        params.append(f'%{name}%')
    act = (action or '').strip()
    if act:
        conditions.append('action = %s')
        params.append(act)
    start = (start_time or '').strip()
    if start:
        conditions.append('create_time >= %s')
        params.append(start)
    end = (end_time or '').strip()
    if end:
        conditions.append('create_time <= %s')
        params.append(end)

    where_sql = f"WHERE {' AND '.join(conditions)}" if conditions else ''

    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                LoginLogMapper.select_page_list(where_sql),
                (*params, start_page, page_size),
            )
            datas = cursor.fetchall()
            cursor.execute(LoginLogMapper.select_total_count(where_sql), tuple(params))
            total_count = cursor.fetchone().get('num', 0)
            return datas, total_count


_HEADING_RE = re.compile(r'^##\s+(\S+)\s*-\s*(\d{4}-\d{2}-\d{2})\s*$')


def _changelog_candidates():
    env_path = os.environ.get('XXGCMS_CHANGELOG_PATH', '').strip()
    paths = []
    if env_path:
        paths.append(env_path)
    paths.append(os.path.join(settings.PROJECT_DIR, 'docs', 'CHANGELOG.md'))
    repo_root = os.path.dirname(settings.PROJECT_DIR)
    paths.append(os.path.join(repo_root, 'docs', 'CHANGELOG.md'))
    return paths


def resolve_changelog_path():
    for path in _changelog_candidates():
        if path and os.path.isfile(path):
            return path
    return None


def get_changelog():
    path = resolve_changelog_path()
    if not path:
        return []

    with open(path, encoding='utf-8') as fh:
        lines = fh.read().splitlines()

    entries = []
    current = None
    for line in lines:
        heading = _HEADING_RE.match(line.strip())
        if heading:
            if current:
                entries.append(current)
            current = {
                'version': heading.group(1),
                'date': heading.group(2),
                'items': [],
            }
            continue
        if current is None:
            continue
        stripped = line.strip()
        if stripped.startswith('- '):
            current['items'].append(stripped[2:].strip())
        elif stripped.startswith('* '):
            current['items'].append(stripped[2:].strip())

    if current:
        entries.append(current)
    return entries
