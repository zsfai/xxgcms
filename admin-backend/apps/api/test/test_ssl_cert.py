# coding: utf-8
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from apps.api.utils.ssl_cert import (
    cert_covers_domains,
    normalize_domain,
    parse_aliases,
    validate_cert_key_pair,
    validate_ssl_material,
)

FIXTURES = Path(__file__).resolve().parent / 'fixtures'


def _other_ca_pem() -> str:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'Fake Intermediate CA')])
    now = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=30))
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')


class SslCertTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fullchain = (FIXTURES / 'sample_fullchain.pem').read_text(encoding='utf-8')
        cls.privkey = (FIXTURES / 'sample_privkey.pem').read_text(encoding='utf-8')

    def test_normalize_domain(self):
        self.assertEqual(normalize_domain('  WWW.XXG.AI  '), 'www.xxg.ai')

    def test_parse_aliases(self):
        self.assertEqual(parse_aliases(' www.xxg.ai, xxg.ai '), ['www.xxg.ai', 'xxg.ai'])

    def test_cert_key_pair(self):
        validate_cert_key_pair(self.fullchain, self.privkey)

    def test_cert_covers_domains(self):
        ok, msg = cert_covers_domains(self.fullchain, ['xxg.ai', 'www.xxg.ai'])
        self.assertTrue(ok, msg)

    def test_cert_missing_domain(self):
        ok, msg = cert_covers_domains(self.fullchain, ['other.com'])
        self.assertFalse(ok)
        self.assertIn('other.com', msg)

    def test_validate_ssl_material(self):
        info = validate_ssl_material(self.fullchain, self.privkey, ['xxg.ai'])
        self.assertIn('not_after', info)

    def test_fullchain_uses_leaf_not_intermediate(self):
        """域名证 + 中间 CA 时，应与私钥匹配第一段，而非最后一段。"""
        chain = self.fullchain.strip() + '\n' + _other_ca_pem()
        validate_cert_key_pair(chain, self.privkey)


if __name__ == '__main__':
    unittest.main()
