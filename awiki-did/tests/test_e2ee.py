"""E2EE 客户端单元测试。"""

import pytest
from cryptography.hazmat.primitives.asymmetric import ec

from sdk.e2ee import E2eeClient, _generate_secp256r1_pem, _load_secp256r1_pem


class TestGenerateSecp256r1Pem:
    """测试密钥生成辅助函数。"""

    def test_returns_pem_string_and_key(self):
        pem_str, key = _generate_secp256r1_pem()
        assert isinstance(pem_str, str)
        assert "BEGIN PRIVATE KEY" in pem_str
        assert isinstance(key, ec.EllipticCurvePrivateKey)

    def test_key_uses_secp256r1_curve(self):
        _, key = _generate_secp256r1_pem()
        assert isinstance(key.curve, ec.SECP256R1)


class TestE2eeClientInit:
    """测试 E2eeClient 初始化。"""

    def test_local_did_set(self):
        client = E2eeClient("did:wba:localhost:user:alice")
        assert client.local_did == "did:wba:localhost:user:alice"

    def test_has_active_session_initial_false(self):
        client = E2eeClient("did:wba:localhost:user:alice")
        assert client.has_active_session("did:wba:localhost:user:bob") is False


class TestE2eeClientEncryptDecryptErrors:
    """测试无活跃会话时的错误。"""

    def test_encrypt_without_session_raises(self):
        client = E2eeClient("did:wba:localhost:user:alice")
        with pytest.raises(RuntimeError, match="没有与"):
            client.encrypt_message("did:wba:localhost:user:bob", "hello")

    def test_decrypt_missing_secret_key_id_raises(self):
        client = E2eeClient("did:wba:localhost:user:alice")
        with pytest.raises(RuntimeError, match="secret_key_id"):
            client.decrypt_message({"encrypted": "data"})


class TestE2eeHandshakeAndEncryption:
    """测试完整握手流程和加解密（Alice <-> Bob）。"""

    def test_full_handshake_and_roundtrip(self):
        alice_did = "did:wba:localhost:user:alice"
        bob_did = "did:wba:localhost:user:bob"

        alice = E2eeClient(alice_did)
        bob = E2eeClient(bob_did)

        # Step 1: Alice 发起握手 -> source_hello
        msg_type, source_hello = alice.initiate_handshake(bob_did)
        assert msg_type == "e2ee_hello"

        # Step 2: Bob 处理 source_hello -> [dest_hello, finished]
        bob_responses = bob.process_e2ee_message(msg_type, source_hello)
        assert len(bob_responses) == 2
        dest_hello_type, dest_hello_content = bob_responses[0]
        bob_finished_type, bob_finished_content = bob_responses[1]

        # Step 3: Alice 处理 dest_hello -> [finished]
        alice_responses = alice.process_e2ee_message(dest_hello_type, dest_hello_content)
        assert len(alice_responses) == 1
        alice_finished_type, alice_finished_content = alice_responses[0]

        # Step 4: Bob 处理 Alice 的 finished -> 会话激活
        bob_final = bob.process_e2ee_message(alice_finished_type, alice_finished_content)
        assert bob_final == []

        # Step 5: Alice 处理 Bob 的 finished -> 会话激活
        alice_final = alice.process_e2ee_message(bob_finished_type, bob_finished_content)
        assert alice_final == []

        # 双方都应该有活跃会话
        assert alice.has_active_session(bob_did) is True
        assert bob.has_active_session(alice_did) is True

        # Alice -> Bob 加密/解密
        _, encrypted = alice.encrypt_message(bob_did, "Hello Bob!")
        original_type, plaintext = bob.decrypt_message(encrypted)
        assert original_type == "text"
        assert plaintext == "Hello Bob!"

        # Bob -> Alice 加密/解密
        _, encrypted2 = bob.encrypt_message(alice_did, "Hi Alice!")
        original_type2, plaintext2 = alice.decrypt_message(encrypted2)
        assert original_type2 == "text"
        assert plaintext2 == "Hi Alice!"


class TestE2eeClientSigningPemReuse:
    """测试 signing_pem 复用行为。"""

    def test_without_signing_pem_generates_new_key(self):
        c1 = E2eeClient("did:wba:localhost:user:alice")
        c2 = E2eeClient("did:wba:localhost:user:alice")
        assert c1._signing_pem != c2._signing_pem

    def test_with_signing_pem_reuses_key(self):
        pem, _ = _generate_secp256r1_pem()
        c1 = E2eeClient("did:wba:localhost:user:alice", signing_pem=pem)
        c2 = E2eeClient("did:wba:localhost:user:alice", signing_pem=pem)
        assert c1._signing_pem == c2._signing_pem == pem

    def test_reused_key_is_valid_secp256r1(self):
        pem, _ = _generate_secp256r1_pem()
        client = E2eeClient("did:wba:localhost:user:alice", signing_pem=pem)
        assert isinstance(client._signing_key, ec.EllipticCurvePrivateKey)
        assert isinstance(client._signing_key.curve, ec.SECP256R1)


class TestE2eeClientExportImport:
    """测试完整握手 → 导出 → 恢复 → 验证加解密仍正常。"""

    @staticmethod
    def _do_full_handshake(alice, bob, alice_did, bob_did):
        """执行完整握手流程，返回双方 ACTIVE 的客户端。"""
        msg_type, source_hello = alice.initiate_handshake(bob_did)
        bob_responses = bob.process_e2ee_message(msg_type, source_hello)
        dest_hello_type, dest_hello_content = bob_responses[0]
        bob_finished_type, bob_finished_content = bob_responses[1]
        alice_responses = alice.process_e2ee_message(dest_hello_type, dest_hello_content)
        alice_finished_type, alice_finished_content = alice_responses[0]
        bob.process_e2ee_message(alice_finished_type, alice_finished_content)
        alice.process_e2ee_message(bob_finished_type, bob_finished_content)

    def test_export_import_roundtrip(self):
        alice_did = "did:wba:localhost:user:alice"
        bob_did = "did:wba:localhost:user:bob"

        alice = E2eeClient(alice_did)
        bob = E2eeClient(bob_did)
        self._do_full_handshake(alice, bob, alice_did, bob_did)

        # 导出 Alice 状态
        alice_state = alice.export_state()
        assert alice_state["local_did"] == alice_did
        assert alice_state["signing_pem"] == alice._signing_pem
        assert len(alice_state["sessions"]) == 1

        # 从 state 恢复 Alice
        alice_restored = E2eeClient.from_state(alice_state)
        assert alice_restored.local_did == alice_did
        assert alice_restored._signing_pem == alice._signing_pem
        assert alice_restored.has_active_session(bob_did) is True

        # 恢复的 Alice 能加密、原始 Bob 能解密
        _, encrypted = alice_restored.encrypt_message(bob_did, "restored msg")
        original_type, plaintext = bob.decrypt_message(encrypted)
        assert original_type == "text"
        assert plaintext == "restored msg"

    def test_export_import_both_sides(self):
        alice_did = "did:wba:localhost:user:alice"
        bob_did = "did:wba:localhost:user:bob"

        alice = E2eeClient(alice_did)
        bob = E2eeClient(bob_did)
        self._do_full_handshake(alice, bob, alice_did, bob_did)

        # 双方都导出再恢复
        alice2 = E2eeClient.from_state(alice.export_state())
        bob2 = E2eeClient.from_state(bob.export_state())

        # 恢复的 Alice -> 恢复的 Bob
        _, enc = alice2.encrypt_message(bob_did, "cross-restore")
        ot, pt = bob2.decrypt_message(enc)
        assert pt == "cross-restore"

        # 恢复的 Bob -> 恢复的 Alice
        _, enc2 = bob2.encrypt_message(alice_did, "reverse")
        ot2, pt2 = alice2.decrypt_message(enc2)
        assert pt2 == "reverse"

    def test_export_no_active_sessions(self):
        client = E2eeClient("did:wba:localhost:user:alice")
        state = client.export_state()
        assert state["sessions"] == []

    def test_from_state_skips_expired_sessions(self):
        alice_did = "did:wba:localhost:user:alice"
        bob_did = "did:wba:localhost:user:bob"

        alice = E2eeClient(alice_did)
        bob = E2eeClient(bob_did)
        self._do_full_handshake(alice, bob, alice_did, bob_did)

        state = alice.export_state()
        # 人为将 active_at 设为很久以前，模拟过期
        state["sessions"][0]["active_at"] = 0.0
        state["sessions"][0]["key_expires"] = 1

        restored = E2eeClient.from_state(state)
        assert restored.has_active_session(bob_did) is False
