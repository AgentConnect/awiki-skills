# awiki-skills

AI 资讯聚合 Claude Code Skills 集合，通过 MCP 协议连接远程服务，获取 AI 领域的最新资讯和活动信息。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## 项目简介

本项目提供了基于 [Claude Code](https://code.claude.com) 的 Skills，通过 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 连接远程服务，实现 AI 资讯的自动获取和活动搜索功能。

### 功能特性

- 📰 **AI 日报摘要**：获取指定日期或最新的 AI 领域新闻日报
- 🔍 **活动搜索**：搜索 AI 相关的活动、会议、研讨会等
- 🔌 **MCP 协议**：基于 MCP Python SDK 实现，支持 streamable-http 传输
- 🚀 **即插即用**：完整的依赖管理和安装脚本
- 🌐 **远程服务**：默认连接 `https://agent-connect.cn/protocol/mcp`

## 快速开始

### 环境要求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv)（推荐）或 pip
- [Claude Code CLI](https://code.claude.com)

### 安装步骤

#### 方式一：让 AI Agent 自动安装（推荐）

在 Claude Code 中直接说：

> 请读取 https://github.com/AgentConnect/awiki-skills/blob/main/INSTALL.md ，按照文档安装这个 skill。

Agent 会自动完成下载、解压、依赖安装和验证，无需手动操作。

#### 方式二：从 GitHub 克隆

```bash
# 克隆仓库
git clone https://github.com/AgentConnect/awiki-skills.git

# 进入 skill 目录
cd awiki-skills/awiki-info

# 安装依赖
uv sync
```

#### 方式三：下载 Release

```bash
# 从 GitHub Releases 下载最新版本
# https://github.com/AgentConnect/awiki-skills/releases

# 解压到你的 skills 目录
unzip awiki-info-v1.0.0.zip -d ~/.claude/skills/

# 安装依赖
cd ~/.claude/skills/awiki-info
uv sync
```

#### 方式四：使用安装脚本

```bash
cd awiki-info
python install_dependencies.py
```

## 使用方法

### 命令行使用

#### 获取 AI 日报

```bash
# 获取最新日报
uv run python scripts/get_daily_summary.py

# 获取指定日期的日报
uv run python scripts/get_daily_summary.py --date 2026-01-27

# 使用自定义 MCP 服务器
uv run python scripts/get_daily_summary.py --server https://your-server/mcp
```

#### 搜索 AI 活动

```bash
# 关键词搜索
uv run python scripts/search_activities.py --keyword "AI Workshop"

# 按状态过滤
uv run python scripts/search_activities.py --keyword "机器学习" --status published

# 搜索未来 30 天的活动
uv run python scripts/search_activities.py --future-days 30

# 完整参数示例
uv run python scripts/search_activities.py \
  --keyword "LLM" \
  --status published \
  --hits 20 \
  --sort-by start_time \
  --sort-order asc
```

### 在 Claude Code 中使用

当你在 Claude Code 中询问 AI 相关资讯时，skill 会自动触发：

**示例对话：**

> **用户**：今天有什么 AI 新闻？
> **Claude**：[自动执行 `get_daily_summary.py` 并返回格式化的日报内容]

> **用户**：搜索一下最近的 AI 会议
> **Claude**：[自动执行 `search_activities.py` 并返回活动列表]

## 项目结构

```
awiki-skills/
├── README.md                       # 项目说明文档
├── LICENSE                         # MIT 许可证
├── publish.py                      # 打包和发布脚本
├── mcp-interace.md                 # MCP 接口文档
└── awiki-info/                     # awiki-info skill
    ├── SKILL.md                    # Skill 配置和文档
    ├── pyproject.toml              # 依赖配置
    ├── uv.lock                     # 依赖锁定文件
    ├── install_dependencies.py     # 安装脚本
    ├── scripts/
    │   ├── __init__.py
    │   ├── mcp_client.py           # MCP 客户端核心模块
    │   ├── get_daily_summary.py    # 日报获取脚本
    │   └── search_activities.py    # 活动搜索脚本
    └── references/
        └── mcp-api.md              # API 参考文档
```

## 配置说明

### MCP 服务器配置

默认 MCP 服务器地址：`https://agent-connect.cn/protocol/mcp`

可通过以下方式自定义：

```bash
# 环境变量
export AWIKI_MCP_SERVER_URL="https://your-server/mcp"

# 命令行参数
python scripts/get_daily_summary.py --server https://your-server/mcp
```

### SKILL.md 配置

`awiki-info/SKILL.md` 包含 skill 的完整配置：

```yaml
---
name: awiki-info
description: AI 资讯聚合服务
allowed-tools: Bash(python:*), Bash(uv:*), Read
---
```

## 开发指南

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/AgentConnect/awiki-skills.git
cd awiki-skills/awiki-info

# 安装开发依赖
uv sync

# 运行测试（如果有）
uv run pytest

# 运行脚本测试
uv run python scripts/get_daily_summary.py
```

### 发布新版本

使用 `publish.py` 脚本一键打包和发布：

```bash
# 完整发布流程（打包 + tag + push + release）
python publish.py

# 仅创建打包文件
python publish.py --skip-tag --skip-push --skip-release

# 指定版本号
python publish.py --version 1.1.0

# 查看帮助
python publish.py --help
```

发布流程：
1. ✅ 检查 git 状态
2. 📦 创建 zip 打包文件
3. 🏷️ 创建 git tag
4. 📤 推送到 GitHub
5. 🚀 创建 GitHub Release（需要 gh CLI）

## API 参考

### MCP 工具

#### get_ai_daily_summary

获取 AI 日报摘要。

**参数：**
- `date` (可选): 日期，格式 `YYYY-MM-DD`，不传则获取最新

**返回：**
- `id`: 摘要 ID
- `summary_date`: 日期
- `content`: Markdown 格式的日报内容
- `feed_count`: 动态数量
- `highlights`: 关键词
- `created_at`: 创建时间

#### search_activities

搜索活动/事件。

**参数：**
- `keyword` (可选): 搜索关键词
- `status` (可选): 活动状态 (draft/published/cancelled)
- `event_type` (可选): 活动类型
- `start_time_min` (可选): 开始时间最小值（Unix 时间戳）
- `start_time_max` (可选): 开始时间最大值（Unix 时间戳）
- `start` (可选): 分页起始位置，默认 0
- `hits` (可选): 返回数量 (1-100)，默认 10
- `sort_by` (可选): 排序字段 (start_time/RANK)
- `sort_order` (可选): 排序方向 (asc/desc)，默认 desc

**返回：**
- `total`: 匹配总数
- `items`: 活动列表

## 常见问题

### 1. 依赖安装失败

**问题**：运行 `uv sync` 失败

**解决方案**：
```bash
# 确保 Python 版本 >= 3.10
python --version

# 尝试使用 pip 安装
pip install mcp>=1.0.0 httpx[socks]
```

### 2. MCP 连接失败

**问题**：执行脚本时提示连接错误

**解决方案**：
- 检查网络连接
- 确认 MCP 服务器地址是否正确
- 尝试使用 `--server` 参数指定服务器地址

### 3. Skill 未被 Claude 触发

**问题**：在 Claude Code 中提问，skill 没有自动执行

**解决方案**：
- 确保 SKILL.md 的 frontmatter 配置正确
- 检查是否在 Claude Code 支持的目录下
- 尝试重启 Claude Code CLI

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 遵循 [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- 使用类型注解
- 添加适当的文档字符串
- 测试代码放在 `tests/` 目录下

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 致谢

- [Claude Code](https://code.claude.com) - Anthropic 官方 CLI 工具
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - MCP 官方 Python SDK
- [uv](https://github.com/astral-sh/uv) - 现代 Python 包管理工具

## 联系方式

- 项目地址：https://github.com/AgentConnect/awiki-skills
- 问题反馈：https://github.com/AgentConnect/awiki-skills/issues
- MCP 服务：https://agent-connect.cn

---

**Built with ❤️ by Claude Code**
