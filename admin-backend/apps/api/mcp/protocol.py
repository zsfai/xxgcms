# coding: utf-8
import uuid

from apps.api.mcp.tools import SERVER_INSTRUCTIONS, TOOL_DEFS, call_tool

PROTOCOL_VERSION = '2025-03-26'
SUPPORTED_VERSIONS = ('2025-03-26', '2024-11-05')


def _rpc_error(req_id, code, message):
    return {
        'jsonrpc': '2.0',
        'id': req_id,
        'error': {'code': code, 'message': message},
    }


def _rpc_result(req_id, result):
    return {
        'jsonrpc': '2.0',
        'id': req_id,
        'result': result,
    }


def handle_message(key_row, message):
    """Return (payload_or_None, is_notification). payload None means 202 empty."""
    if not isinstance(message, dict):
        return _rpc_error(None, -32600, 'Invalid Request'), False

    jsonrpc = message.get('jsonrpc')
    method = message.get('method')
    req_id = message.get('id', None)
    params = message.get('params') if isinstance(message.get('params'), dict) else {}
    is_notification = 'id' not in message

    if jsonrpc != '2.0' or not method:
        if is_notification:
            return None, True
        return _rpc_error(req_id, -32600, 'Invalid Request'), False

    if method == 'notifications/initialized' or method.startswith('notifications/'):
        return None, True

    if is_notification:
        return None, True

    if method == 'initialize':
        client_version = params.get('protocolVersion') or PROTOCOL_VERSION
        version = client_version if client_version in SUPPORTED_VERSIONS else PROTOCOL_VERSION
        return _rpc_result(req_id, {
            'protocolVersion': version,
            'capabilities': {
                'tools': {'listChanged': False},
            },
            'serverInfo': {
                'name': 'xxgcms',
                'version': '2.0.4',
            },
            'instructions': SERVER_INSTRUCTIONS,
        }), False

    if method == 'ping':
        return _rpc_result(req_id, {}), False

    if method == 'tools/list':
        return _rpc_result(req_id, {'tools': TOOL_DEFS}), False

    if method == 'tools/call':
        name = params.get('name') or ''
        arguments = params.get('arguments') or {}
        result = call_tool(key_row, name, arguments)
        return _rpc_result(req_id, result), False

    return _rpc_error(req_id, -32601, 'Method not found: %s' % method), False


def new_session_id():
    return str(uuid.uuid4())
