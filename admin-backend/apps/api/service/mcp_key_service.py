# coding: utf-8
import hashlib
import secrets

from apps.api.db.connection import xxgcms_connection
from apps.api.sql_mapper.base_mapper import BaseMapper
from apps.api.sql_mapper.mcp_key_mapper import McpKeyMapper
from apps.api.utils.public import log_error


def hash_mcp_key(raw_key):
    return hashlib.sha256((raw_key or '').encode('utf-8')).hexdigest()


def _user_id(cursor, user_name):
    cursor.execute(BaseMapper.select_user_by_name(), (user_name,))
    row = cursor.fetchone()
    if not row:
        raise Exception('用户不存在')
    return row.get('id')


def _assert_site_allowed(cursor, user_id, site_id):
    if site_id is None:
        return
    cursor.execute(BaseMapper.select_site_list(), (user_id,))
    allowed = {row.get('id') for row in cursor.fetchall()}
    if site_id not in allowed:
        raise Exception('无权绑定该站点')


def list_keys(user_name):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            user_id = _user_id(cursor, user_name)
            cursor.execute(McpKeyMapper.select_by_user(), (user_id,))
            return cursor.fetchall()


def create_key(user_name, name, site_id=None):
    label = (name or '').strip() or 'MCP Key'
    if len(label) > 64:
        label = label[:64]
    sid = site_id if site_id not in ('', None, 0, '0') else None
    if sid is not None:
        sid = int(sid)

    raw = 'xxg_' + secrets.token_urlsafe(32)
    prefix = raw[:12]
    digest = hash_mcp_key(raw)

    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            user_id = _user_id(cursor, user_name)
            _assert_site_allowed(cursor, user_id, sid)
            cursor.execute(
                McpKeyMapper.insert_key(),
                (user_id, label, prefix, digest, sid),
            )
            key_id = cursor.lastrowid
            conn.commit()
    return {
        'id': key_id,
        'name': label,
        'key': raw,
        'key_prefix': prefix,
        'site_id': sid,
    }


def revoke_key(user_name, key_id):
    kid = int(key_id)
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            user_id = _user_id(cursor, user_name)
            cursor.execute(McpKeyMapper.select_owned(), (kid, user_id))
            row = cursor.fetchone()
            if not row:
                raise Exception('密钥不存在')
            if row.get('enabled') == 'N':
                return True
            cursor.execute(McpKeyMapper.revoke(), (kid, user_id))
            conn.commit()
    return True


def authenticate_mcp_key(raw_key):
    token = (raw_key or '').strip()
    if not token:
        return None, '缺少 MCP Key'
    digest = hash_mcp_key(token)
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(McpKeyMapper.select_by_hash(), (digest,))
            row = cursor.fetchone()
            if not row:
                return None, 'MCP Key 无效'
            if row.get('enabled') != 'Y':
                return None, 'MCP Key 已撤销'
            if row.get('user_status') != 1:
                return None, '用户已停用'
            try:
                cursor.execute(McpKeyMapper.touch_last_used(), (row.get('id'),))
                conn.commit()
            except Exception as exc:
                log_error('更新 MCP Key 最近使用时间失败: %s' % exc)
            return row, ''
