"""共享测试 fixtures。"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import httpx
import pytest

# 将 awiki-did/ 根目录加入 sys.path，使 `from sdk.xxx import` 可用
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from sdk.config import SDKConfig
from sdk.identity import DIDIdentity


@pytest.fixture()
def sdk_config(monkeypatch):
    """返回使用默认值的 SDKConfig（清除环境变量干扰）。"""
    monkeypatch.delenv("E2E_USER_SERVICE_URL", raising=False)
    monkeypatch.delenv("E2E_MOLT_MESSAGE_URL", raising=False)
    monkeypatch.delenv("E2E_DID_DOMAIN", raising=False)
    return SDKConfig()


@pytest.fixture()
def sample_did_identity():
    """用真实 secp256k1 密钥对构造 DIDIdentity。"""
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        NoEncryption,
        PrivateFormat,
        PublicFormat,
    )

    private_key = ec.generate_private_key(ec.SECP256K1())
    private_pem = private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    public_pem = private_key.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)

    return DIDIdentity(
        did="did:wba:localhost:user:test123",
        did_document={"id": "did:wba:localhost:user:test123", "verificationMethod": []},
        private_key_pem=private_pem,
        public_key_pem=public_pem,
    )


@pytest.fixture()
def tmp_credentials_dir(tmp_path, monkeypatch):
    """将 credential_store._CREDENTIALS_DIR 替换为临时目录。"""
    import scripts.credential_store as cs

    monkeypatch.setattr(cs, "_CREDENTIALS_DIR", tmp_path / ".credentials")
    return tmp_path / ".credentials"


@pytest.fixture()
def tmp_e2ee_store(tmp_path, monkeypatch):
    """将 e2ee_store._CREDENTIALS_DIR 替换为临时目录。"""
    import scripts.e2ee_store as es

    monkeypatch.setattr(es, "_CREDENTIALS_DIR", tmp_path / ".credentials")
    return tmp_path / ".credentials"


def _build_httpx_response(
    status_code: int = 200,
    json_body: dict | None = None,
) -> httpx.Response:
    """构造 httpx.Response 对象。"""
    resp = httpx.Response(
        status_code=status_code,
        json=json_body,
        request=httpx.Request("POST", "http://test"),
    )
    return resp


@pytest.fixture()
def mock_httpx_response():
    """返回 _build_httpx_response 工厂函数。"""
    return _build_httpx_response
