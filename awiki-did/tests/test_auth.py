"""认证流程单元测试（mock 网络调用）。"""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from sdk.auth import create_authenticated_identity, get_jwt_via_wba, register_did
from sdk.config import SDKConfig
from sdk.identity import DIDIdentity


class TestRegisterDid:
    """测试 register_did。"""

    async def test_payload_structure(self, sample_did_identity, mock_httpx_response):
        client = AsyncMock(spec=httpx.AsyncClient)

        with patch("sdk.auth.rpc_call", new_callable=AsyncMock) as mock_rpc:
            mock_rpc.return_value = {"did": sample_did_identity.did, "user_id": "u1", "message": "ok"}
            await register_did(client, sample_did_identity)

            mock_rpc.assert_called_once()
            args = mock_rpc.call_args
            assert args[0][1] == "/user-service/did-auth/rpc"
            assert args[0][2] == "register"
            payload = args[0][3]
            assert "did_document" in payload
            assert payload["did_document"] is sample_did_identity.did_document

    async def test_optional_params_forwarded(self, sample_did_identity):
        client = AsyncMock(spec=httpx.AsyncClient)

        with patch("sdk.auth.rpc_call", new_callable=AsyncMock) as mock_rpc:
            mock_rpc.return_value = {"did": "d", "user_id": "u", "message": "ok"}
            await register_did(
                client,
                sample_did_identity,
                name="Alice",
                is_public=True,
                is_agent=True,
            )
            payload = mock_rpc.call_args[0][3]
            assert payload["name"] == "Alice"
            assert payload["is_public"] is True
            assert payload["is_agent"] is True


class TestGetJwtViaWba:
    """测试 get_jwt_via_wba。"""

    async def test_returns_access_token(self, sample_did_identity):
        client = AsyncMock(spec=httpx.AsyncClient)

        with patch("sdk.auth.rpc_call", new_callable=AsyncMock) as mock_rpc, \
             patch("sdk.auth.generate_auth_header", return_value="DIDWba fake-header"):
            mock_rpc.return_value = {"access_token": "jwt_abc123"}
            token = await get_jwt_via_wba(client, sample_did_identity, "localhost")

        assert token == "jwt_abc123"
        mock_rpc.assert_called_once()
        args = mock_rpc.call_args
        assert args[0][2] == "verify"
        assert "authorization" in args[0][3]


class TestCreateAuthenticatedIdentity:
    """测试 create_authenticated_identity 完整流程。"""

    async def test_full_flow(self, sdk_config):
        client = AsyncMock(spec=httpx.AsyncClient)

        with patch("sdk.auth.create_identity") as mock_create, \
             patch("sdk.auth.rpc_call", new_callable=AsyncMock) as mock_rpc, \
             patch("sdk.auth.generate_auth_header", return_value="DIDWba hdr"):

            # create_identity 返回 mock identity
            from cryptography.hazmat.primitives.asymmetric import ec
            from cryptography.hazmat.primitives.serialization import (
                Encoding, NoEncryption, PrivateFormat, PublicFormat,
            )
            key = ec.generate_private_key(ec.SECP256K1())
            priv_pem = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
            pub_pem = key.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
            mock_identity = DIDIdentity(
                did="did:wba:localhost:user:test_xxx",
                did_document={"id": "did:wba:localhost:user:test_xxx"},
                private_key_pem=priv_pem,
                public_key_pem=pub_pem,
            )
            mock_create.return_value = mock_identity

            # rpc_call 依次返回 register 和 verify 结果
            mock_rpc.side_effect = [
                {"did": mock_identity.did, "user_id": "uid_42", "message": "registered"},
                {"access_token": "jwt_final"},
            ]

            result = await create_authenticated_identity(
                client, sdk_config, unique_id="test_xxx", name="Bot"
            )

        assert result.user_id == "uid_42"
        assert result.jwt_token == "jwt_final"
        assert result.did == "did:wba:localhost:user:test_xxx"
        assert mock_rpc.call_count == 2
