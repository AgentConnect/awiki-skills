# awiki-did/

> L2 文档 | 父级: [../CLAUDE.md](../CLAUDE.md) | 分形协议: 三层结构

1. **地位**: DID 去中心化身份交互 Skill，为 Claude Code 提供 DID 身份管理、消息通信、社交关系、E2EE 加密通信能力
2. **边界**:
   - **输入**: 用户指令（创建身份、发送消息、管理关系等）、环境变量配置
   - **输出**: DID 操作结果（身份信息、消息、关系状态等）、本地凭证文件
3. **约束**:
   - 必须使用 ANP >= 0.5.3 作为 DID 和 E2EE 底层实现
   - DID 身份使用 secp256k1 密钥，E2EE 使用 secp256r1 密钥
   - 私钥文件权限必须设为 600
   - 所有网络请求必须异步（async/await）
   - 凭证目录 `.credentials/` 必须在 `.gitignore` 中忽略

## 成员清单

**SKILL.md**: Skill 配置文档（触发场景、使用说明、工具权限、路径约定、CLI 示例）

**pyproject.toml**: 项目依赖配置（anp>=0.5.3、httpx>=0.28.0）

**install_dependencies.py**: 多选安装脚本（支持 uv/pip 两种方式）

**.gitignore**: 忽略 .credentials/、__pycache__ 等

### sdk/ - Bundle 的 awiki_sdk

**__init__.py**: 公共 API 导出（SDKConfig, DIDIdentity, create_identity, register_did, get_jwt_via_wba, generate_wba_auth_header, create_authenticated_identity, create_user_service_client, create_molt_message_client, rpc_call, JsonRpcError, E2eeClient）

**config.py**: SDKConfig dataclass（user_service_url, molt_message_url, did_domain，从环境变量加载）

**identity.py**: DIDIdentity 数据类 + create_identity() 封装 ANP + load_private_key()

**auth.py**: register_did()、get_jwt_via_wba()、generate_wba_auth_header()、create_authenticated_identity()

**client.py**: httpx AsyncClient 工厂（create_user_service_client, create_molt_message_client）

**rpc.py**: JSON-RPC 2.0 客户端（rpc_call(), JsonRpcError）

**e2ee.py**: E2EE 端到端加密客户端（E2eeClient），支持握手/加解密/状态导出恢复（export_state/from_state），跨进程持久化

### scripts/ - 可执行脚本层

**credential_store.py**: 凭证持久化模块（save_identity, load_identity, list_identities, delete_identity, update_jwt）

**setup_identity.py**: DID 身份创建/加载/列出/删除（CLI 入口）

**get_profile.py**: 查看 Profile（自己/公开/DID 解析）

**update_profile.py**: 更新 Profile（昵称、简介、标签、Markdown）

**send_message.py**: 发送消息给指定 DID

**check_inbox.py**: 查看收件箱、聊天历史、标记已读

**manage_relationship.py**: 关注/取关/查看关系状态/关注列表/粉丝列表

**manage_group.py**: 创建群组/邀请/加入/查看成员

**e2ee_messaging.py**: E2EE 握手/加密消息发送/收件箱处理，集成 e2ee_store 实现跨进程状态持久化

**e2ee_store.py**: E2EE 状态持久化模块（save_e2ee_state, load_e2ee_state, delete_e2ee_state），与 credential_store 共用 .credentials/ 目录

### tests/ - 单元测试

**conftest.py**: 共享 fixtures（sdk_config、sample_did_identity、tmp_credentials_dir、mock_httpx_response）

**test_config.py**: SDKConfig 默认值、环境变量覆盖、frozen 不可变性测试

**test_rpc.py**: JSON-RPC 2.0 调用成功/错误/payload 格式验证

**test_identity.py**: DIDIdentity 属性、load_private_key、create_identity（mock ANP）测试

**test_client.py**: httpx 客户端工厂 base_url/timeout/trust_env 测试

**test_auth.py**: register_did/get_jwt_via_wba/create_authenticated_identity 流程测试（mock 网络）

**test_e2ee.py**: E2EE 密钥生成、握手流程、加解密往返、signing_pem 复用、状态导出/恢复 round-trip 测试

**test_credential_store.py**: 凭证 CRUD、文件权限、JWT 更新测试（tmp 目录）

**test_e2ee_store.py**: E2EE 状态持久化 round-trip、文件权限验证、删除操作测试

### references/ - API 参考文档

**did-auth-api.md**: DID 注册与认证 RPC 规范

**profile-api.md**: Profile 管理 RPC 规范

**messaging-api.md**: 消息收发 RPC 规范

**relationship-api.md**: 社交关系与群组 RPC 规范

**e2ee-protocol.md**: E2EE 加密协议规范

⚡触发器: 一旦本文件夹增删文件或架构逻辑调整，请立即重写此文档。
