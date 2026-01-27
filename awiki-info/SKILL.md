---
name: awiki-info
description: |
  AI 资讯聚合服务。获取最新 AI 领域新闻日报、搜索 AI 相关活动和事件。
  触发场景：用户询问 AI 新闻/资讯、想了解 AI 领域动态、需要 AI 热点汇总、
  搜索 AI 相关的活动/会议/研讨会等。
allowed-tools: Bash(python:*), Bash(uv:*), Read
---

# AI 资讯聚合 Skill

通过 MCP 协议连接远程服务，获取 AI 领域的最新资讯和活动信息。

## 环境要求

首次使用前需安装依赖：

```bash
cd /Users/cs/work/agents/awiki-skills/awiki-info && uv sync
```

或使用安装脚本：

```bash
cd /Users/cs/work/agents/awiki-skills/awiki-info && python install_dependencies.py
```

## 可用功能

### 1. 获取 AI 日报摘要

获取指定日期或最新的 AI 新闻日报汇总。

**使用方法**：

```bash
# 获取最新日报
python /Users/cs/work/agents/awiki-skills/awiki-info/scripts/get_daily_summary.py

# 获取指定日期的日报
python /Users/cs/work/agents/awiki-skills/awiki-info/scripts/get_daily_summary.py --date 2026-01-27
```

**返回内容**：
- 汇总日期
- Markdown 格式的日报内容（包含今日概览、分类汇总、重点推荐）
- 当日动态数量
- 重点关键词

### 2. 搜索 AI 活动

搜索 AI 相关的活动、会议、研讨会等事件。

**使用方法**：

```bash
# 关键词搜索
python /Users/cs/work/agents/awiki-skills/awiki-info/scripts/search_activities.py --keyword "AI Workshop"

# 按状态过滤（draft/published/cancelled）
python /Users/cs/work/agents/awiki-skills/awiki-info/scripts/search_activities.py --keyword "机器学习" --status published

# 按时间范围筛选（未来30天内的活动）
python /Users/cs/work/agents/awiki-skills/awiki-info/scripts/search_activities.py --future-days 30

# 完整参数示例
python /Users/cs/work/agents/awiki-skills/awiki-info/scripts/search_activities.py \
  --keyword "LLM" \
  --status published \
  --hits 20 \
  --sort-by start_time \
  --sort-order asc
```

**支持的参数**：
- `--keyword`: 搜索关键词
- `--status`: 活动状态 (draft/published/cancelled)
- `--event-type`: 活动类型
- `--future-days`: 搜索未来 N 天内的活动
- `--hits`: 返回数量 (1-100，默认10)
- `--start`: 分页起始位置
- `--sort-by`: 排序字段 (start_time/RANK)
- `--sort-order`: 排序方向 (asc/desc)

**返回内容**：
- 匹配的活动总数
- 活动列表（包含标题、主办方、地点、时间、详情链接等）

## MCP 服务器配置

默认连接 `https://agent-connect.cn/awiki/mcp`，可通过环境变量或命令行参数指定：

```bash
# 环境变量方式
export AWIKI_MCP_SERVER_URL="https://your-server/mcp"

# 命令行参数方式
python scripts/get_daily_summary.py --server https://your-server/mcp
```

## 典型对话示例

**用户**: "帮我看看今天有什么 AI 新闻"
→ 执行 `python scripts/get_daily_summary.py`，返回格式化的日报内容

**用户**: "获取 2026-01-20 的 AI 资讯"
→ 执行 `python scripts/get_daily_summary.py --date 2026-01-20`

**用户**: "搜索一下最近有什么 AI 相关的活动"
→ 执行 `python scripts/search_activities.py --future-days 30 --status published`

**用户**: "查找关于大模型的研讨会"
→ 执行 `python scripts/search_activities.py --keyword "大模型" --status published`

## 错误处理

如遇到连接错误，请检查：
1. 网络连接是否正常
2. MCP 服务器地址是否正确
3. 依赖是否已正确安装

## 参考文档

详细的 MCP API 规范请参阅 [references/mcp-api.md](references/mcp-api.md)
