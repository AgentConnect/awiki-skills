"""DIDIdentity 和 create_identity 单元测试。"""

from unittest.mock import patch

import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from sdk.identity import DIDIdentity, create_identity, load_private_key


class TestDIDIdentity:
    """测试 DIDIdentity 数据类。"""

    def test_unique_id_extracts_last_segment(self, sample_did_identity):
        assert sample_did_identity.unique_id == "test123"

    def test_unique_id_single_segment(self):
        identity = DIDIdentity(
            did="did:wba:localhost:abc",
            did_document={},
            private_key_pem=b"",
            public_key_pem=b"",
        )
        assert identity.unique_id == "abc"

    def test_get_private_key_returns_ec_key(self, sample_did_identity):
        key = sample_did_identity.get_private_key()
        assert isinstance(key, ec.EllipticCurvePrivateKey)


class TestLoadPrivateKey:
    """测试 load_private_key 函数。"""

    def test_valid_ec_pem(self, sample_did_identity):
        key = load_private_key(sample_did_identity.private_key_pem)
        assert isinstance(key, ec.EllipticCurvePrivateKey)

    def test_non_ec_key_raises_type_error(self):
        from cryptography.hazmat.primitives.asymmetric import rsa

        rsa_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        rsa_pem = rsa_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
        with pytest.raises(TypeError, match="EllipticCurvePrivateKey"):
            load_private_key(rsa_pem)


class TestCreateIdentity:
    """测试 create_identity 函数（mock ANP）。"""

    def test_returns_did_identity(self):
        private_key = ec.generate_private_key(ec.SECP256K1())
        priv_pem = private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
        pub_pem = private_key.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)

        fake_doc = {"id": "did:wba:localhost:user:alice", "verificationMethod": []}
        fake_keys = {"key-1": (priv_pem, pub_pem)}

        with patch("sdk.identity.create_did_wba_document", return_value=(fake_doc, fake_keys)):
            identity = create_identity("localhost", ["user", "alice"])

        assert isinstance(identity, DIDIdentity)
        assert identity.did == "did:wba:localhost:user:alice"
        assert identity.private_key_pem == priv_pem
        assert identity.public_key_pem == pub_pem
        assert identity.did_document is fake_doc
