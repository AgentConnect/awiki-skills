"""JSON-RPC 客户端单元测试。"""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from sdk.rpc import JsonRpcError, rpc_call


class TestRpcCallSuccess:
    """测试成功调用。"""

    async def test_returns_result(self, mock_httpx_response):
        client = AsyncMock(spec=httpx.AsyncClient)
        client.post.return_value = mock_httpx_response(
            json_body={"jsonrpc": "2.0", "result": {"ok": True}, "id": 1}
        )
        result = await rpc_call(client, "/rpc", "test_method", {"key": "val"})
        assert result == {"ok": True}

    async def test_request_payload_format(self, mock_httpx_response):
        client = AsyncMock(spec=httpx.AsyncClient)
        client.post.return_value = mock_httpx_response(
            json_body={"jsonrpc": "2.0", "result": "ok", "id": 1}
        )
        await rpc_call(client, "/rpc", "my_method", {"a": 1}, request_id=42)

        client.post.assert_called_once_with(
            "/rpc",
            json={
                "jsonrpc": "2.0",
                "method": "my_method",
                "params": {"a": 1},
                "id": 42,
            },
        )

    async def test_params_none_defaults_to_empty_dict(self, mock_httpx_response):
        client = AsyncMock(spec=httpx.AsyncClient)
        client.post.return_value = mock_httpx_response(
            json_body={"jsonrpc": "2.0", "result": "ok", "id": 1}
        )
        await rpc_call(client, "/rpc", "m")

        _, kwargs = client.post.call_args
        assert kwargs["json"]["params"] == {}


class TestRpcCallError:
    """测试错误场景。"""

    async def test_jsonrpc_error_raises(self, mock_httpx_response):
        client = AsyncMock(spec=httpx.AsyncClient)
        client.post.return_value = mock_httpx_response(
            json_body={
                "jsonrpc": "2.0",
                "error": {"code": -32600, "message": "Invalid Request", "data": {"detail": "x"}},
                "id": 1,
            }
        )
        with pytest.raises(JsonRpcError) as exc_info:
            await rpc_call(client, "/rpc", "bad")

        err = exc_info.value
        assert err.code == -32600
        assert err.message == "Invalid Request"
        assert err.data == {"detail": "x"}

    async def test_http_error_raises(self):
        client = AsyncMock(spec=httpx.AsyncClient)
        resp = httpx.Response(
            status_code=500,
            request=httpx.Request("POST", "http://test/rpc"),
        )
        client.post.return_value = resp
        with pytest.raises(httpx.HTTPStatusError):
            await rpc_call(client, "/rpc", "fail")


class TestJsonRpcError:
    """测试 JsonRpcError 属性和字符串表示。"""

    def test_str_representation(self):
        err = JsonRpcError(-32601, "Method not found", {"hint": "check name"})
        assert "-32601" in str(err)
        assert "Method not found" in str(err)
        assert err.data == {"hint": "check name"}
