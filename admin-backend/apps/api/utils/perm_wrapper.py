# -*- coding:utf-8 -*-
from django.http import JsonResponse

from apps.api.service import token_service


def perm(**kwargs):
    def fn(function=None):
        def wrapper(request, *args, **kwargs):
            try:
                token = request.META.get('HTTP_AUTH_KEY')
                user_name, msg = token_service.token_auth(token)
                if user_name is None:
                    return JsonResponse({'code': 403, 'message': msg})
                request.xxgcms_user = user_name
                return function(request, *args, **kwargs)
            except Exception as exc:
                return JsonResponse({
                    'code': 403,
                    'message': f'验证失败：{exc}',
                })
        return wrapper
    return fn
