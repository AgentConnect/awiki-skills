# AI News MCP Server 接口规范

此文档定义了 AI 资讯聚合 Skill 所依赖的 MCP Server 接口规范。

## 服务概述

MCP Server 通过 HTTP Streaming 模式提供服务，暴露两个 Tools 供 Claude 调用。

## Tools 定义

### Tool 1: get_ai_news

获取 AI 领域资讯汇总。

#### 输入 Schema

```json
{
  "name": "get_ai_news",
  "description": "获取 AI 领域的最新资讯汇总",
  "inputSchema": {
    "type": "object",
    "properties": {
      "date": {
        "type": "string",
        "description": "查询日期，格式 YYYY-MM-DD。不传则返回最新资讯。",
        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
      }
    },
    "required": []
  }
}
```

#### 输出格式

返回 Markdown 格式的资讯汇总，结构如下：

```markdown
# AI 资讯日报 - 2025-01-27

## 今日热点

1. **[热点标题1]** - 简短摘要...
2. **[热点标题2]** - 简短摘要...
3. **[热点标题3]** - 简短摘要...

## 详细内容

### OpenAI Blog

- **[文章标题](原文链接)**
  摘要内容...

### Anthropic Blog

- **[文章标题](原文链接)**
  摘要内容...

### 其他信源...

## 当前订阅信源

- OpenAI Blog (https://openai.com/blog/rss)
- Anthropic Blog (https://www.anthropic.com/rss.xml)
- ...
```

---

### Tool 2: feedback

自然语言交互接口，支持订阅管理和内容深入查询。

#### 输入 Schema

```json
{
  "name": "feedback",
  "description": "自然语言交互接口，支持订阅管理、内容查询等操作",
  "inputSchema": {
    "type": "object",
    "properties": {
      "message": {
        "type": "string",
        "description": "用户的自然语言输入"
      }
    },
    "required": ["message"]
  }
}
```

#### 支持的操作类型

| 操作类型 | 示例消息 | 预期行为 |
|---------|---------|---------|
| 添加订阅 | "添加 https://example.com/rss 作为新订阅源" | 验证 URL 有效性，添加到订阅列表 |
| 删除订阅 | "取消订阅 OpenAI Blog" | 从订阅列表中移除指定源 |
| 列出订阅 | "显示当前所有订阅源" | 返回订阅源列表 |
| 深入查询 | "详细介绍 xxx 这条新闻" | 返回指定新闻的详细内容 |
| 搜索内容 | "搜索关于 GPT-5 的新闻" | 在已抓取内容中搜索 |

#### 输出格式

根据操作类型返回不同格式的响应：

**添加/删除订阅成功**:
```markdown
✓ 操作成功

已添加订阅源: Example Blog
URL: https://example.com/rss

当前订阅数: 10
```

**深入查询**:
```markdown
# [文章标题]

**来源**: OpenAI Blog
**发布时间**: 2025-01-27
**原文链接**: https://...

## 内容摘要

详细内容...

## 相关资讯

- [相关文章1](链接)
- [相关文章2](链接)
```

---

## MCP Server 配置示例

用户需要在 `~/.claude.json` 中添加如下配置：

```json
{
  "mcpServers": {
    "ai-news": {
      "command": "python",
      "args": ["-m", "ai_news_mcp.server"],
      "env": {}
    }
  }
}
```

或者使用 HTTP 远程服务：

```json
{
  "mcpServers": {
    "ai-news": {
      "url": "http://localhost:8000/mcp",
      "transport": "http-stream"
    }
  }
}
```

---

## 预置信源建议

建议 MCP Server 预置以下高质量 AI 信源：

| 信源名称 | RSS URL | 类型 |
|---------|---------|------|
| OpenAI Blog | https://openai.com/blog/rss | 官方博客 |
| Anthropic Blog | https://www.anthropic.com/rss.xml | 官方博客 |
| DeepMind Blog | https://deepmind.google/blog/rss.xml | 官方博客 |
| Hugging Face Blog | https://huggingface.co/blog/feed.xml | 技术博客 |
| AI News (Hacker News) | https://hnrss.org/newest?q=AI | 社区 |
| 机器之心 | https://www.jiqizhixin.com/rss | 中文媒体 |
| 量子位 | https://www.qbitai.com/feed | 中文媒体 |
