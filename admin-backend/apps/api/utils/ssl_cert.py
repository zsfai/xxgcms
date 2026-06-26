# coding: utf-8
"""PEM 证书解析与域名匹配校验。"""
import re
from datetime import timezone

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.x509.oid import NameOID

_DOMAIN_RE = re.compile(
    r'^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)*[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$'
)


def normalize_domain(value: str) -> str:
    return (value or '').strip().lower().rstrip('.')


def validate_domain(value: str) -> str:
    domain = normalize_domain(value)
    if not domain or not _DOMAIN_RE.match(domain):
        raise ValueError(f'域名格式不合法: {value!r}')
    return domain


def parse_aliases(raw: str) -> list[str]:
    aliases = []
    for part in (raw or '').split(','):
        part = part.strip()
        if not part:
            continue
        domain = validate_domain(part)
        if domain not in aliases:
            aliases.append(domain)
    return aliases


def normalize_pem_text(text: str) -> str:
    """粘贴内容常见 \\r\\n、BOM、首尾空白。"""
    return (text or '').strip().lstrip('\ufeff').replace('\r\n', '\n').replace('\r', '\n')


def load_leaf_certificate(fullchain_pem: str):
    if not normalize_pem_text(fullchain_pem):
        raise ValueError('证书内容不能为空')
    blocks = _split_pem_blocks(normalize_pem_text(fullchain_pem), 'CERTIFICATE')
    if not blocks:
        raise ValueError('未找到有效的 CERTIFICATE PEM 块')
    # fullchain 标准顺序：域名证书在前，中间 CA 在后（阿里云 / Let's Encrypt 均如此）
    return x509.load_pem_x509_certificate(blocks[0].encode('utf-8'))


def _split_pem_blocks(text: str, label: str) -> list[str]:
    begin = f'-----BEGIN {label}-----'
    end = f'-----END {label}-----'
    blocks = []
    start = 0
    while True:
        i = text.find(begin, start)
        if i < 0:
            break
        j = text.find(end, i)
        if j < 0:
            raise ValueError(f'PEM 块不完整: {label}')
        blocks.append(text[i:j + len(end)])
        start = j + len(end)
    return blocks


def parse_certificate_pem(fullchain_pem: str) -> dict:
    cert = load_leaf_certificate(fullchain_pem)
    not_after = cert.not_valid_after_utc.replace(tzinfo=timezone.utc)
    san_dns = []
    try:
        san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        san_dns = [normalize_domain(name) for name in san.value.get_values_for_type(x509.DNSName)]
    except x509.ExtensionNotFound:
        pass

    common_name = ''
    for attr in cert.subject:
        if attr.oid == NameOID.COMMON_NAME:
            common_name = normalize_domain(attr.value)
            break

    return {
        'not_after': not_after,
        'san_dns_names': san_dns,
        'common_name': common_name,
    }


def validate_private_key_pem(privkey_pem: str) -> None:
    text = normalize_pem_text(privkey_pem)
    if not text:
        raise ValueError('私钥内容不能为空')
    try:
        serialization.load_pem_private_key(text.encode('utf-8'), password=None)
    except TypeError as exc:
        raise ValueError('私钥已加密，请粘贴解密后的 PEM（不含密码）') from exc
    except ValueError as exc:
        raise ValueError(f'私钥格式无效: {exc}') from exc


def _public_key_der(public_key) -> bytes:
    return public_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)


def validate_cert_key_pair(fullchain_pem: str, privkey_pem: str) -> None:
    cert = load_leaf_certificate(fullchain_pem)
    private_key = serialization.load_pem_private_key(
        normalize_pem_text(privkey_pem).encode('utf-8'),
        password=None,
    )
    if _public_key_der(cert.public_key()) != _public_key_der(private_key.public_key()):
        raise ValueError(
            '证书与私钥不匹配。请确认：'
            '① 证书链第一个 PEM 为域名证书；'
            '② 私钥为申请该证书时生成的 .key；'
            '③ 阿里云请用「Nginx」格式，证书链 = 域名证书 + 中间证书拼接'
        )


def _wildcard_match(pattern: str, domain: str) -> bool:
    pattern = normalize_domain(pattern)
    domain = normalize_domain(domain)
    if pattern == domain:
        return True
    if pattern.startswith('*.'):
        suffix = pattern[1:]
        return domain.endswith(suffix) and domain != pattern[2:]
    return False


def _domain_covered(domain: str, cert_info: dict) -> bool:
    domain = normalize_domain(domain)
    candidates = set(cert_info.get('san_dns_names') or [])
    cn = cert_info.get('common_name') or ''
    if cn:
        candidates.add(cn)
    for pattern in candidates:
        if _wildcard_match(pattern, domain):
            return True
    return False


def cert_covers_domains(fullchain_pem: str, domains: list[str]) -> tuple[bool, str]:
    cert_info = parse_certificate_pem(fullchain_pem)
    missing = [d for d in domains if not _domain_covered(d, cert_info)]
    if missing:
        return False, f'证书未覆盖以下域名: {", ".join(missing)}'
    return True, ''


def validate_ssl_material(fullchain_pem: str, privkey_pem: str, domains: list[str]) -> dict:
    validate_cert_key_pair(fullchain_pem, privkey_pem)
    ok, msg = cert_covers_domains(fullchain_pem, domains)
    if not ok:
        raise ValueError(msg)
    return parse_certificate_pem(fullchain_pem)
