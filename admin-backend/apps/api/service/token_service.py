# coding: utf-8
import arrow
from itsdangerous import BadData, BadSignature, SignatureExpired, URLSafeTimedSerializer

from apps.settings import AUTH_SALT, EXPIRES_TIME, SECRET_KEY
from apps.api.utils.public import log_debug, log_error


class AccessToken:
    def __init__(self, **kwargs):
        self.user_name = kwargs.get('user_name')

    def _serializer(self, expires_in=None):
        return URLSafeTimedSerializer(
            secret_key=SECRET_KEY,
            salt=AUTH_SALT,
        )

    def gen_token_seq(self, expires):
        log_debug(f'过期时间: {expires} 秒')
        payload = {
            'user_name': self.user_name,
            'iat': int(arrow.now().timestamp()),
        }
        return self._serializer().dumps(payload)

    def token_auth(self, token):
        log_debug('开始验证 token')
        if not token:
            return None, '令牌有误，请登录验证'
        try:
            data = self._serializer().loads(token, max_age=EXPIRES_TIME)
        except SignatureExpired:
            return None, '令牌已失效'
        except BadSignature as exc:
            if exc.payload is not None:
                try:
                    self._serializer().loads(exc.payload)
                except BadData:
                    return None, '验证失败，无权访问'
            return None, '签名存在问题'
        except BadData:
            return None, '令牌有误，请登录验证'

        user_name = data.get('user_name')
        if not user_name:
            return None, '存在不合法的参数'
        log_debug(f'验证 token 成功: {user_name}')
        return user_name, f'用户({user_name})令牌验证成功.'


def create_token(name):
    log_debug('生成 token')
    try:
        return AccessToken(user_name=name).gen_token_seq(EXPIRES_TIME)
    except Exception as exc:
        log_error(f'生成 token 失败：{exc}')


def token_auth(token):
    log_debug('验证 token')
    try:
        return AccessToken().token_auth(token)
    except Exception as exc:
        log_error(f'验证 token 出现错误：{exc}')
        return '', str(exc)
