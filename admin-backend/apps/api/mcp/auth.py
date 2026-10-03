# coding: utf-8


def extract_mcp_key(request):
    auth = request.META.get('HTTP_AUTHORIZATION') or ''
    if auth.lower().startswith('bearer '):
        return auth[7:].strip()
    header_key = request.META.get('HTTP_X_MCP_KEY') or ''
    if header_key.strip():
        return header_key.strip()
    return ''
