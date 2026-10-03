# coding: utf-8
import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from apps.api.mcp.auth import extract_mcp_key
from apps.api.mcp.protocol import handle_message, new_session_id
from apps.api.service import mcp_key_service

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS, GET',
    'Access-Control-Allow-Headers': (
        'Authorization, Content-Type, Mcp-Session-Id, MCP-Protocol-Version, X-MCP-Key'
    ),
    'Access-Control-Max-Age': '86400',
}


def _apply_headers(response, request):
    for key, value in CORS_HEADERS.items():
        response[key] = value
    session_id = request.META.get('HTTP_MCP_SESSION_ID') or new_session_id()
    response['Mcp-Session-Id'] = session_id
    response['MCP-Protocol-Version'] = request.META.get('HTTP_MCP_PROTOCOL_VERSION') or '2025-03-26'
    return response


@csrf_exempt
def mcp_endpoint(request):
    if request.method == 'OPTIONS':
        return _apply_headers(HttpResponse(status=204), request)
    if request.method == 'GET':
        resp = HttpResponse('Streamable HTTP MCP: POST JSON-RPC only', status=405, content_type='text/plain')
        resp['Allow'] = 'POST, OPTIONS'
        return _apply_headers(resp, request)
    if request.method != 'POST':
        return _apply_headers(HttpResponse(status=405), request)

    raw_key = extract_mcp_key(request)
    key_row, err = mcp_key_service.authenticate_mcp_key(raw_key)
    if key_row is None:
        resp = JsonResponse({'error': err or 'unauthorized'}, status=401)
        return _apply_headers(resp, request)

    try:
        if not request.body:
            body = {}
        else:
            body = json.loads(request.body)
    except json.JSONDecodeError:
        resp = JsonResponse(
            {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32700, 'message': 'Parse error'}},
            status=400,
        )
        return _apply_headers(resp, request)

    if isinstance(body, list):
        payloads = []
        all_notes = True
        for item in body:
            payload, is_note = handle_message(key_row, item)
            if not is_note:
                all_notes = False
            if payload is not None:
                payloads.append(payload)
        if all_notes and not payloads:
            return _apply_headers(HttpResponse(status=202), request)
        resp = JsonResponse(payloads, safe=False, json_dumps_params={'ensure_ascii': False})
        return _apply_headers(resp, request)

    payload, is_note = handle_message(key_row, body)
    if is_note and payload is None:
        return _apply_headers(HttpResponse(status=202), request)
    resp = JsonResponse(payload, json_dumps_params={'ensure_ascii': False})
    return _apply_headers(resp, request)
