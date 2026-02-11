# awiki-info/

> L2 文档 | 父级: [../CLAUDE.md](../CLAUDE.md) | 分形协议: 三层结构

1. **地位**: AI 资讯聚合 Skill，通过 MCP 协议连接远程服务，为 Claude Code 提供 AI 领域资讯能力
2. **边界**:
   - **输入**: 用户查询意图（AI 新闻、活动搜索）、日期参数、搜索关键词
   - **输出**: AI 日报摘要（Markdown 格式）、活动列表（结构化数据）
3. **约束**:
   - 必须使用 MCP SDK 1.0+ 连接远程服务
   - 所有网络请求必须异步（async/await）
   - 远程服务 URL 可通过环境变量 `AWIKI_MCP_SERVER_URL` 配置
   - 必须支持命令行和程序化两种调用方式

## 成员清单

**SKILL.md**: Skill 配置文档（触发场景、使用说明、工具权限、路径约定——使用 SKILL_DIR 相对路径，无硬编码）

**pyproject.toml**: 项目依赖配置（uv 包管理、Python 3.10+）

**install_dependencies.py**: 多选安装脚本（支持 uv/pip 两种方式）

### scripts/ - 可执行脚本层

**mcp_client.py**: MCP 客户端核心（MCPClient 类、异步工具调用、服务器连接管理）

**get_daily_summary.py**: 日报获取命令行脚本（支持日期参数、自定义服务器）

**search_activities.py**: 活动搜索命令行脚本（支持关键词、状态、类型、排序等多维度搜索）

**__init__.py**: 模块导出和 API 接口暴露（MCPClient、get_ai_daily_summary、search_activities）

### references/ - 文档和 API 参考

**mcp-api.md**: MCP 服务接口规范（get_ai_daily_summary、search_activities 工具文档）

⚡触发器: 一旦本文件夹增删文件或架构逻辑调整，请立即重写此文档。
