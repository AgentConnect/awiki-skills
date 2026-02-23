"""凭证持久化单元测试（使用 tmp_path）。"""

import json
import os
import stat

import pytest

from scripts.credential_store import (
    delete_identity,
    list_identities,
    load_identity,
    save_identity,
    update_jwt,
)


class TestSaveIdentity:
    """测试 save_identity。"""

    def test_creates_file_and_returns_path(self, tmp_credentials_dir):
        path = save_identity(
            did="did:wba:localhost:user:abc",
            unique_id="abc",
            user_id="u1",
            private_key_pem=b"-----BEGIN PRIVATE KEY-----\nfake\n-----END PRIVATE KEY-----",
            public_key_pem=b"-----BEGIN PUBLIC KEY-----\nfake\n-----END PUBLIC KEY-----",
            name="test_cred",
        )
        assert path.exists()
        assert path.name == "test_cred.json"

    def test_file_permission_600(self, tmp_credentials_dir):
        path = save_identity(
            did="did:wba:localhost:user:abc",
            unique_id="abc",
            user_id="u1",
            private_key_pem=b"fake-key",
            public_key_pem=b"fake-pub",
            name="perm_test",
        )
        file_mode = os.stat(path).st_mode & 0o777
        assert file_mode == 0o600

    def test_dir_permission_700(self, tmp_credentials_dir):
        save_identity(
            did="did:wba:localhost:user:abc",
            unique_id="abc",
            user_id="u1",
            private_key_pem=b"fake-key",
            public_key_pem=b"fake-pub",
            name="dir_test",
        )
        dir_mode = os.stat(tmp_credentials_dir).st_mode & 0o777
        assert dir_mode == 0o700

    def test_json_content_fields(self, tmp_credentials_dir):
        path = save_identity(
            did="did:wba:localhost:user:abc",
            unique_id="abc",
            user_id="u1",
            private_key_pem=b"priv-pem",
            public_key_pem=b"pub-pem",
            jwt_token="jwt123",
            display_name="Alice",
            name="content_test",
        )
        data = json.loads(path.read_text())
        assert data["did"] == "did:wba:localhost:user:abc"
        assert data["unique_id"] == "abc"
        assert data["user_id"] == "u1"
        assert data["private_key_pem"] == "priv-pem"
        assert data["public_key_pem"] == "pub-pem"
        assert data["jwt_token"] == "jwt123"
        assert data["name"] == "Alice"
        assert "created_at" in data

    def test_bytes_pem_converted_to_str(self, tmp_credentials_dir):
        path = save_identity(
            did="did:wba:localhost:user:abc",
            unique_id="abc",
            user_id=None,
            private_key_pem=b"bytes-key",
            public_key_pem=b"bytes-pub",
            name="bytes_test",
        )
        data = json.loads(path.read_text())
        assert isinstance(data["private_key_pem"], str)
        assert isinstance(data["public_key_pem"], str)


class TestLoadIdentity:
    """测试 load_identity。"""

    def test_load_saved_identity(self, tmp_credentials_dir):
        save_identity(
            did="did:wba:localhost:user:load",
            unique_id="load",
            user_id="u2",
            private_key_pem=b"key",
            public_key_pem=b"pub",
            name="load_test",
        )
        data = load_identity("load_test")
        assert data is not None
        assert data["did"] == "did:wba:localhost:user:load"

    def test_load_nonexistent_returns_none(self, tmp_credentials_dir):
        assert load_identity("nonexistent") is None


class TestListIdentities:
    """测试 list_identities。"""

    def test_empty_dir_returns_empty_list(self, tmp_credentials_dir):
        assert list_identities() == []

    def test_multiple_identities(self, tmp_credentials_dir):
        for i in range(3):
            save_identity(
                did=f"did:wba:localhost:user:u{i}",
                unique_id=f"u{i}",
                user_id=f"uid{i}",
                private_key_pem=b"k",
                public_key_pem=b"p",
                name=f"id_{i}",
            )
        result = list_identities()
        assert len(result) == 3
        names = [r["credential_name"] for r in result]
        assert sorted(names) == ["id_0", "id_1", "id_2"]


class TestDeleteIdentity:
    """测试 delete_identity。"""

    def test_delete_existing(self, tmp_credentials_dir):
        save_identity(
            did="did:wba:localhost:user:del",
            unique_id="del",
            user_id="u3",
            private_key_pem=b"k",
            public_key_pem=b"p",
            name="to_delete",
        )
        assert delete_identity("to_delete") is True
        assert load_identity("to_delete") is None

    def test_delete_nonexistent_returns_false(self, tmp_credentials_dir):
        assert delete_identity("no_such") is False


class TestUpdateJwt:
    """测试 update_jwt。"""

    def test_update_existing(self, tmp_credentials_dir):
        save_identity(
            did="did:wba:localhost:user:jwt",
            unique_id="jwt",
            user_id="u4",
            private_key_pem=b"k",
            public_key_pem=b"p",
            jwt_token="old_token",
            name="jwt_test",
        )
        assert update_jwt("jwt_test", "new_token") is True
        data = load_identity("jwt_test")
        assert data["jwt_token"] == "new_token"

    def test_update_nonexistent_returns_false(self, tmp_credentials_dir):
        assert update_jwt("no_such", "token") is False
