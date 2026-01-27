# MCP 工具 API 文档

## 概述

本文档描述了协议网关提供的 MCP（模型上下文协议）工具。这些工具允许 MCP 客户端访问 AI 日报摘要和搜索活动。

## 服务器信息

| 属性 | 值 |
|----------|-------|
| 服务器名称 | Protocol Gateway MCP Server |
| 协议 | MCP (Model Context Protocol) |
| 传输方式 | streamable-http |
| 默认端口 | 8000 |
| 默认路径 | /mcp |

## 工具

### 1. get_ai_daily_summary

获取 AI 新闻日报摘要。

#### 描述

获取指定日期或最新的 AI 新闻日报汇总。日报包含当日的动态汇总、分类信息和重点推荐。

#### 输入参数

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|-----------|------|----------|---------|-------------|
| `date` | str | 否 | None | 日期，格式为 YYYY-MM-DD。不提供则返回最新日报 |

#### 输出

返回日报摘要对象：

```json
{
    "id": "sum_xyz789abc",
    "summary_date": "2026-01-21",
    "content": "# 2026-01-21 当日动态汇总日报\n\n## 1) 今日概览\n...",
    "feed_count": 411,
    "highlights": {
        "sections": ["今日概览", "分类汇总", "重点推荐"],
        "keywords": ["AI", "ChatGPT apps", "分发渠道"]
    },
    "created_at": "2026-01-22T12:17:44+00:00"
}
```

#### 字段描述

| 字段 | 类型 | 描述 |
|-------|------|-------------|
| `id` | string | 日报唯一标识，格式 `sum_xxx` |
| `summary_date` | string | 汇总日期（YYYY-MM-DD） |
| `content` | string | 汇总内容（Markdown 格式） |
| `feed_count` | integer | 当日动态数量 |
| `highlights` | object | 重点信息，包含 sections 和 keywords 数组 |
| `created_at` | string | 生成时间（ISO8601 格式） |

#### 使用示例

```python
# 获取最新日报
result = await tool_get_ai_daily_summary()

# 获取指定日期的日报
result = await tool_get_ai_daily_summary(date="2026-01-21")
```

#### 错误

| 错误 | 描述 |
|-------|-------------|
| SummaryNotFoundError | 日报不存在（HTTP 404） |
| InvalidDateFormatError | 日期格式无效，应为 YYYY-MM-DD |
| Service Unavailable | 内部摘要服务不可用 |

---

### 2. search_activities

搜索活动/事件。

#### 描述

使用 OpenSearch 搜索活动，支持关键词搜索、状态过滤、时间范围筛选和排序。

#### 输入参数

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|-----------|------|----------|---------|-------------|
| `keyword` | str | 否 | None | 搜索关键词 |
| `status` | str | 否 | None | 活动状态：`draft`、`published`、`cancelled` |
| `event_type` | str | 否 | None | 活动类型过滤 |
| `start_time_min` | int | 否 | None | 开始时间最小值（Unix 时间戳） |
| `start_time_max` | int | 否 | None | 开始时间最大值（Unix 时间戳） |
| `start` | int | 否 | 0 | 分页起始位置（>= 0） |
| `hits` | int | 否 | 10 | 返回数量（1-100） |
| `sort_by` | str | 否 | None | 排序字段或 `RANK`（相关性排序） |
| `sort_order` | str | 否 | desc | 排序方向：`asc` 或 `desc` |

#### 输出

返回搜索结果对象：

```json
{
    "total": 42,
    "items": [
        {
            "id": "activity_001",
            "title": "AI Workshop 2024",
            "organizer": "Tech Community",
            "location": "Shanghai",
            "speaker": "John Doe",
            "tags": "AI,workshop",
            "event_time": "2024-03-15 14:00",
            "status": "published",
            "event_type": "workshop",
            "start_time": 1710489600,
            "end_time": 1710500400,
            "source_url": "https://example.com/event/001",
            "poster_url": "https://example.com/poster/001.jpg",
            "details": {
                "description": "Learn about the latest AI technologies...",
                "target_audience": "Developers and AI enthusiasts",
                "registration_url": "https://example.com/register",
                "speakers": [
                    {"name": "John Doe", "title": "AI Research Lead"}
                ],
                "agenda": ["09:00 - Opening remarks", "10:00 - Workshop"],
                "highlights": ["Interactive sessions", "Networking"],
                "other_info": "Lunch provided"
            }
        }
    ],
    "request_id": "16XXXXXXXXXXXXXX"
}
```

#### 字段描述

**顶层字段：**

| 字段 | 类型 | 描述 |
|-------|------|-------------|
| `total` | integer | 匹配的活动总数 |
| `items` | array | 活动列表 |
| `request_id` | string | OpenSearch 请求 ID（用于排查问题） |

**活动项字段：**

| 字段 | 类型 | 描述 |
|-------|------|-------------|
| `id` | string | 活动唯一标识 |
| `title` | string | 活动标题 |
| `organizer` | string | 主办方名称 |
| `location` | string | 活动地点 |
| `speaker` | string | 嘉宾/讲者 |
| `tags` | string | 标签（逗号分隔） |
| `event_time` | string | 活动时间描述 |
| `status` | string | 活动状态 |
| `event_type` | string | 活动类型 |
| `start_time` | integer | 开始时间（Unix 时间戳） |
| `end_time` | integer | 结束时间（Unix 时间戳） |
| `source_url` | string | 原始来源链接 |
| `poster_url` | string | 海报图片链接 |
| `details` | object | 活动详情（可选） |

**活动详情字段（details）：**

| 字段 | 类型 | 描述 |
|-------|------|-------------|
| `description` | string | 活动描述 |
| `target_audience` | string | 目标人群 |
| `registration_url` | string | 报名链接 |
| `speakers` | array | 嘉宾信息列表 `[{name, title}]` |
| `agenda` | array | 活动议程 |
| `highlights` | array | 活动亮点 |
| `other_info` | string | 其他信息 |

#### 使用示例

```python
# 搜索 AI 相关的已发布活动
result = await tool_search_activities(keyword="AI", status="published")

# 按相关性排序搜索
result = await tool_search_activities(
    keyword="机器学习",
    sort_by="RANK",
    hits=20
)

# 按时间范围筛选
import time
now = int(time.time())
one_month_later = now + 30 * 24 * 3600
result = await tool_search_activities(
    start_time_min=now,
    start_time_max=one_month_later,
    sort_by="start_time",
    sort_order="asc"
)
```

#### 错误

| 错误 | 描述 |
|-------|-------------|
| ValueError | 无效的 status 或 sort_order 参数 |
| Service Unavailable | 内部活动搜索服务不可用 |

---

## 内部 HTTP API 依赖

MCP 工具依赖以下内部 HTTP API：

### AI 日报服务 API

| 属性 | 值 |
|----------|-------|
| Base URL | `http://localhost:9893` |
| 按日期查询 | `GET /summaries/{date}` |
| 最新日报 | `GET /summaries/latest` |

**成功响应（HTTP 200）：**

```json
{
    "summary": {
        "id": "sum_xyz789abc",
        "summary_date": "2026-01-21",
        "content": "# 日报内容...",
        "feed_count": 411,
        "highlights": {
            "sections": ["今日概览"],
            "keywords": ["AI"]
        },
        "created_at": "2026-01-22T12:17:44Z"
    }
}
```

**错误响应：**

```json
{
    "error": {
        "code": 404,
        "message": "日报不存在"
    }
}
```

### 活动搜索服务 API

| 属性 | 值 |
|----------|-------|
| Base URL | `http://localhost:9895` |
| 搜索端点 | `GET /api/v1/activities/search` |

**查询参数：**

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `keyword` | str | 搜索关键词 |
| `status` | str | 活动状态 |
| `event_type` | str | 活动类型 |
| `start_time_min` | int | 开始时间最小值 |
| `start_time_max` | int | 开始时间最大值 |
| `start` | int | 分页起始 |
| `hits` | int | 返回数量 |
| `sort_by` | str | 排序字段 |
| `sort_order` | str | 排序方向 |

**响应格式：**

```json
{
    "total": 42,
    "items": [...],
    "request_id": "16XXXXXXXXXXXXXX"
}
```

---

## 配置

MCP 服务器可以通过环境变量进行配置：

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `MCP_SERVER_NAME` | Protocol Gateway MCP Server | 服务器名称 |
| `MCP_HOST` | 0.0.0.0 | 服务器主机 |
| `MCP_PORT` | 8000 | 服务器端口 |
| `MCP_PATH` | /mcp | 服务器路径 |
| `GATEWAY_SUMMARY_API_BASE_URL` | http://localhost:9893 | 日报服务 URL |
| `GATEWAY_ACTIVITY_API_BASE_URL` | http://localhost:9895 | 活动搜索服务 URL |
| `GATEWAY_HTTP_TIMEOUT` | 30.0 | HTTP 客户端超时时间（秒） |

---

## 运行服务器

```bash
# 使用 uv
uv run python -m protocol_gateway.mcp.server

# 或在激活虚拟环境后
python -m protocol_gateway.mcp.server
```

服务器将默认在 `http://0.0.0.0:8000/mcp` 上启动。
