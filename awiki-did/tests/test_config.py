"""SDKConfig 单元测试。"""

import pytest

from sdk.config import SDKConfig


class TestSDKConfigDefaults:
    """测试默认值（无环境变量时）。"""

    def test_default_user_service_url(self, sdk_config):
        assert sdk_config.user_service_url == "https://awiki.info"

    def test_default_molt_message_url(self, sdk_config):
        assert sdk_config.molt_message_url == "https://awiki.info"

    def test_default_did_domain(self, sdk_config):
        assert sdk_config.did_domain == "awiki.info"


class TestSDKConfigEnvOverride:
    """测试环境变量覆盖。"""

    def test_user_service_url_from_env(self, monkeypatch):
        monkeypatch.setenv("E2E_USER_SERVICE_URL", "http://custom:1111")
        monkeypatch.delenv("E2E_MOLT_MESSAGE_URL", raising=False)
        monkeypatch.delenv("E2E_DID_DOMAIN", raising=False)
        config = SDKConfig()
        assert config.user_service_url == "http://custom:1111"

    def test_molt_message_url_from_env(self, monkeypatch):
        monkeypatch.delenv("E2E_USER_SERVICE_URL", raising=False)
        monkeypatch.setenv("E2E_MOLT_MESSAGE_URL", "http://custom:2222")
        monkeypatch.delenv("E2E_DID_DOMAIN", raising=False)
        config = SDKConfig()
        assert config.molt_message_url == "http://custom:2222"

    def test_did_domain_from_env(self, monkeypatch):
        monkeypatch.delenv("E2E_USER_SERVICE_URL", raising=False)
        monkeypatch.delenv("E2E_MOLT_MESSAGE_URL", raising=False)
        monkeypatch.setenv("E2E_DID_DOMAIN", "example.com")
        config = SDKConfig()
        assert config.did_domain == "example.com"


class TestSDKConfigFrozen:
    """测试 frozen dataclass 不可修改。"""

    def test_cannot_set_attribute(self, sdk_config):
        with pytest.raises(AttributeError):
            sdk_config.user_service_url = "http://should-fail"
