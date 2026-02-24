"""E2EE 状态持久化单元测试。"""

import json
import os
import stat

import pytest


class TestE2eeStoreRoundTrip:
    """保存/加载 round-trip 测试。"""

    def test_save_and_load(self, tmp_e2ee_store):
        from scripts.e2ee_store import save_e2ee_state, load_e2ee_state

        state = {
            "local_did": "did:wba:localhost:user:alice",
            "signing_pem": "-----BEGIN PRIVATE KEY-----\nfake\n-----END PRIVATE KEY-----",
            "sessions": [
                {
                    "session_id": "abc123",
                    "local_did": "did:wba:localhost:user:alice",
                    "peer_did": "did:wba:localhost:user:bob",
                    "send_key": "AAAA",
                    "recv_key": "BBBB",
                    "secret_key_id": "key_001",
                }
            ],
        }
        save_e2ee_state(state, "test_cred")
        loaded = load_e2ee_state("test_cred")
        assert loaded is not None
        assert loaded["local_did"] == state["local_did"]
        assert loaded["signing_pem"] == state["signing_pem"]
        assert len(loaded["sessions"]) == 1
        assert loaded["sessions"][0]["session_id"] == "abc123"

    def test_load_nonexistent_returns_none(self, tmp_e2ee_store):
        from scripts.e2ee_store import load_e2ee_state

        assert load_e2ee_state("nonexistent") is None


class TestE2eeStoreFilePermissions:
    """文件权限验证测试。"""

    def test_file_permission_600(self, tmp_e2ee_store):
        from scripts.e2ee_store import save_e2ee_state, _e2ee_state_path

        save_e2ee_state({"local_did": "test", "signing_pem": "", "sessions": []}, "perm_test")
        path = _e2ee_state_path("perm_test")
        file_mode = stat.S_IMODE(os.stat(path).st_mode)
        assert file_mode == (stat.S_IRUSR | stat.S_IWUSR)

    def test_directory_permission_700(self, tmp_e2ee_store):
        from scripts.e2ee_store import save_e2ee_state, _CREDENTIALS_DIR

        save_e2ee_state({"local_did": "test", "signing_pem": "", "sessions": []}, "dir_test")
        # tmp_e2ee_store 已经 monkeypatch 了 _CREDENTIALS_DIR
        from scripts import e2ee_store
        dir_mode = stat.S_IMODE(os.stat(e2ee_store._CREDENTIALS_DIR).st_mode)
        assert dir_mode == stat.S_IRWXU


class TestE2eeStoreDelete:
    """删除操作测试。"""

    def test_delete_existing(self, tmp_e2ee_store):
        from scripts.e2ee_store import save_e2ee_state, load_e2ee_state, delete_e2ee_state

        save_e2ee_state({"local_did": "test", "signing_pem": "", "sessions": []}, "del_test")
        assert load_e2ee_state("del_test") is not None
        assert delete_e2ee_state("del_test") is True
        assert load_e2ee_state("del_test") is None

    def test_delete_nonexistent_returns_false(self, tmp_e2ee_store):
        from scripts.e2ee_store import delete_e2ee_state

        assert delete_e2ee_state("no_such_state") is False
