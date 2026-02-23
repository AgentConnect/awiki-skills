"""E2EE 端到端加密客户端（封装 ANP e2e_encryption_v2）。

[INPUT]: ANP E2eeSession / E2eeKeyManager / detect_message_type, local_did
[OUTPUT]: E2eeClient 类，提供握手、加密、解密的高层 API
[POS]: 封装 ANP 底层 E2EE 协议，为上层应用提供简洁的加解密接口

[PROTOCOL]:
1. 逻辑变更时同步更新此头部
2. 更新后检查所在文件夹的 CLAUDE.md
"""

from __future__ import annotations

import logging
from typing import Any

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)

from anp.e2e_encryption_v2 import (
    E2eeKeyManager,
    E2eeSession,
    SessionState,
    detect_message_type,
)

logger = logging.getLogger(__name__)


def _generate_secp256r1_pem() -> tuple[str, ec.EllipticCurvePrivateKey]:
    """生成 secp256r1 密钥对，返回 (pem_str, private_key_obj)。"""
    private_key = ec.generate_private_key(ec.SECP256R1())
    pem_bytes = private_key.private_bytes(
        Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
    )
    return pem_bytes.decode("utf-8"), private_key


class E2eeClient:
    """E2EE 端到端加密客户端。

    封装 ANP ``E2eeSession`` 和 ``E2eeKeyManager``，提供：
    - 握手发起与协议消息处理
    - 消息加密与解密
    - 过期会话清理

    关键设计：E2EE 协议使用 secp256r1 曲线（ECDHE 临时密钥 + proof 签名密钥），
    与 DID 身份密钥（secp256k1）分离。构造函数自动生成独立的 secp256r1 签名密钥。
    """

    def __init__(self, local_did: str) -> None:
        """初始化 E2EE 客户端。

        Args:
            local_did: 本地 DID 标识符。
        """
        self.local_did = local_did
        self._signing_pem, self._signing_key = _generate_secp256r1_pem()
        self._key_manager = E2eeKeyManager()

    def initiate_handshake(self, peer_did: str) -> tuple[str, dict[str, Any]]:
        """发起 E2EE 握手。

        创建新的 ``E2eeSession``，生成 SourceHello 消息。

        Args:
            peer_did: 对端 DID 标识符。

        Returns:
            ``(msg_type, content_dict)`` 元组，调用方负责序列化后通过 RPC 发送。
            msg_type 为 ``"e2ee_hello"``。
        """
        session = E2eeSession(
            local_did=self.local_did,
            did_private_key_pem=self._signing_pem,
            peer_did=peer_did,
        )
        msg_type, content = session.initiate_handshake()
        self._key_manager.register_pending_session(session)
        return msg_type, content

    def process_e2ee_message(
        self, msg_type: str, content: dict[str, Any]
    ) -> list[tuple[str, dict[str, Any]]]:
        """处理收到的 E2EE 协议消息。

        根据消息类型执行对应操作，返回需要发送给对端的响应消息列表。

        Args:
            msg_type: 消息类型（``e2ee_hello`` / ``e2ee_finished`` / ``e2ee_error``）。
            content: 消息内容 dict。

        Returns:
            需要发送的消息列表，每项为 ``(msg_type, content_dict)``。
            可能 0~2 条：

            - source_hello → 返回 ``[dest_hello, finished]``
            - destination_hello → 返回 ``[finished]``
            - finished → 返回 ``[]``（会话激活）
            - error → 返回 ``[]``
        """
        detected = detect_message_type(msg_type, content)
        if detected is None:
            logger.warning("无法识别的 E2EE 消息类型: %s", msg_type)
            return []

        if detected == "source_hello":
            return self._handle_source_hello(content)
        elif detected == "destination_hello":
            return self._handle_destination_hello(content)
        elif detected == "finished":
            return self._handle_finished(content)
        elif detected == "error":
            return self._handle_error(content)
        elif detected == "encrypted":
            logger.warning("process_e2ee_message 不处理加密消息，请使用 decrypt_message")
            return []
        else:
            logger.warning("未处理的 E2EE 消息子类型: %s", detected)
            return []

    def has_active_session(self, peer_did: str) -> bool:
        """检查是否存在与指定对端的活跃加密会话。

        Args:
            peer_did: 对端 DID 标识符。

        Returns:
            存在活跃（ACTIVE 且未过期）会话时返回 ``True``。
        """
        session = self._key_manager.get_active_session(self.local_did, peer_did)
        return session is not None

    def encrypt_message(
        self, peer_did: str, plaintext: str, original_type: str = "text"
    ) -> tuple[str, dict[str, Any]]:
        """加密消息。

        Args:
            peer_did: 对端 DID 标识符。
            plaintext: 明文内容。
            original_type: 原始消息类型（默认 ``"text"``）。

        Returns:
            ``(msg_type, content_dict)`` 元组，msg_type 为 ``"e2ee"``。

        Raises:
            RuntimeError: 没有与对端的活跃会话。
        """
        session = self._key_manager.get_active_session(self.local_did, peer_did)
        if session is None:
            raise RuntimeError(f"没有与 {peer_did} 的活跃 E2EE 会话")
        return session.encrypt_message(original_type, plaintext)

    def decrypt_message(self, content: dict[str, Any]) -> tuple[str, str]:
        """解密消息。

        根据 ``secret_key_id`` 查找对应的会话并解密。

        Args:
            content: 加密消息的 content dict（含 ``secret_key_id``、``encrypted`` 等）。

        Returns:
            ``(original_type, plaintext)`` 元组。

        Raises:
            RuntimeError: 找不到对应的会话。
        """
        secret_key_id = content.get("secret_key_id")
        if not secret_key_id:
            raise RuntimeError("消息缺少 secret_key_id")

        session = self._key_manager.get_session_by_key_id(secret_key_id)
        if session is None:
            raise RuntimeError(f"找不到 secret_key_id={secret_key_id} 对应的会话")
        return session.decrypt_message(content)

    def cleanup_expired(self) -> list[tuple[str, str]]:
        """清理过期会话。

        Returns:
            需要重新握手的 ``(local_did, peer_did)`` 列表。
        """
        return self._key_manager.cleanup_expired()

    # ------------------------------------------------------------------
    # 内部处理方法
    # ------------------------------------------------------------------

    def _handle_source_hello(
        self, content: dict[str, Any]
    ) -> list[tuple[str, dict[str, Any]]]:
        """处理 SourceHello：创建 responder 会话，返回 [dest_hello, finished]。"""
        peer_did = content.get("source_did", "")
        session = E2eeSession(
            local_did=self.local_did,
            did_private_key_pem=self._signing_pem,
            peer_did=peer_did,
        )
        (hello_type, hello_content), (finished_type, finished_content) = (
            session.process_source_hello(content)
        )
        # responder 在 process_source_hello 后进入 HANDSHAKE_COMPLETING 状态
        self._key_manager.register_pending_session(session)
        return [(hello_type, hello_content), (finished_type, finished_content)]

    def _handle_destination_hello(
        self, content: dict[str, Any]
    ) -> list[tuple[str, dict[str, Any]]]:
        """处理 DestinationHello：查找 pending session，返回 [finished]。"""
        session_id = content.get("session_id", "")
        session = self._key_manager.get_pending_session(session_id)
        if session is None:
            logger.warning("找不到 session_id=%s 的握手会话", session_id)
            return []

        finished_type, finished_content = session.process_destination_hello(content)
        return [(finished_type, finished_content)]

    def _handle_finished(
        self, content: dict[str, Any]
    ) -> list[tuple[str, dict[str, Any]]]:
        """处理 Finished：激活会话。"""
        session_id = content.get("session_id", "")
        session = self._key_manager.get_pending_session(session_id)
        if session is None:
            logger.warning("找不到 session_id=%s 的握手会话", session_id)
            return []

        session.process_finished(content)
        if session.state == SessionState.ACTIVE:
            self._key_manager.promote_pending_session(session_id)
            logger.info(
                "E2EE 会话激活: %s <-> %s (session_id=%s)",
                session.local_did,
                session.peer_did,
                session_id,
            )
        return []

    def _handle_error(
        self, content: dict[str, Any]
    ) -> list[tuple[str, dict[str, Any]]]:
        """处理 E2EE Error：记录日志，返回空列表。"""
        error_code = content.get("error_code", "unknown")
        secret_key_id = content.get("secret_key_id", "")
        logger.warning(
            "收到 E2EE 错误: code=%s, secret_key_id=%s", error_code, secret_key_id
        )
        # 如果是密钥过期或找不到，移除对应会话
        session = self._key_manager.get_session_by_key_id(secret_key_id)
        if session is not None:
            self._key_manager.remove_session(session)
        return []


__all__ = ["E2eeClient"]
