"""httpx 客户端工厂单元测试。"""

from sdk.client import create_molt_message_client, create_user_service_client
from sdk.config import SDKConfig


class TestCreateUserServiceClient:
    """测试 create_user_service_client。"""

    def test_base_url(self, sdk_config):
        client = create_user_service_client(sdk_config)
        assert str(client.base_url) == "http://localhost:9891"

    def test_timeout(self, sdk_config):
        client = create_user_service_client(sdk_config)
        assert client.timeout.connect == 30.0

    def test_trust_env_disabled(self, sdk_config):
        client = create_user_service_client(sdk_config)
        assert client._trust_env is False


class TestCreateMoltMessageClient:
    """测试 create_molt_message_client。"""

    def test_base_url(self, sdk_config):
        client = create_molt_message_client(sdk_config)
        assert str(client.base_url) == "http://localhost:9898"

    def test_custom_config(self, monkeypatch):
        monkeypatch.delenv("E2E_USER_SERVICE_URL", raising=False)
        monkeypatch.delenv("E2E_MOLT_MESSAGE_URL", raising=False)
        monkeypatch.delenv("E2E_DID_DOMAIN", raising=False)
        config = SDKConfig(
            user_service_url="http://custom:1111",
            molt_message_url="http://custom:2222",
        )
        us_client = create_user_service_client(config)
        mm_client = create_molt_message_client(config)
        assert str(us_client.base_url) == "http://custom:1111"
        assert str(mm_client.base_url) == "http://custom:2222"
