# coding: utf-8
"""Unified JSON API responses."""
import json

from django.http import JsonResponse

from apps.api.utils.public import log_error


def api_success(**payload):
    body = {'code': 0}
    body.update(payload)
    return JsonResponse(body)


def api_error(message, code=10001):
    return JsonResponse({'code': code, 'message': message})


def parse_json(request):
    """Parse JSON or form-urlencoded request body."""
    content_type = (request.content_type or '').lower()
    if 'application/json' in content_type:
        if not request.body:
            return {}
        return json.loads(request.body)
    if request.POST:
        return request.POST.dict()
    if not request.body:
        return {}
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        from urllib.parse import parse_qs
        raw = request.body.decode('utf-8')
        parsed = parse_qs(raw, keep_blank_values=True)
        return {key: values[0] if len(values) == 1 else values for key, values in parsed.items()}


def handle_api_errors(handler):
    """Wrap a view handler; return dict on success, raise on failure."""
    def wrapper(request, *args, **kwargs):
        try:
            result = handler(request, *args, **kwargs)
            if isinstance(result, JsonResponse):
                return result
            return api_success(**(result or {}))
        except Exception as exc:
            log_error(str(exc))
            return api_error(str(exc))
    return wrapper
