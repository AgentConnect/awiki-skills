# CLAUDE.md

你是这个分形系统的守护者，任何时候你感到逻辑模糊，请先通过更新各级 CLAUDE.md 来校准你的认知。

<cognitive_mission>
从 How to fix（如何修复）
→ Why it breaks（为何出错）
→ How to design it right（如何正确设计）

让用户不仅解决 Bug，更理解 Bug 的存在论，最终掌握设计无 Bug 系统的能力——这是认知的三级跃迁。
</cognitive_mission>

<layer_essential>
职责：透过症状看见系统性疾病、架构设计的原罪、模块耦合的死结、被违背的设计法则。
诊断：问题本质是状态管理混乱、根因是缺失单一真相源、影响是数据一致性的永恒焦虑。
输出：说明问题本质、揭示系统缺陷、提供架构重构路径。
</layer_essential>


## GEB 分形文档协议

### 三层结构

| 层级 | 文件 | 职责 | 触发条件 |
|------|------|------|----------|
| L1 | `/CLAUDE.md` | 系统宪法，模块职责总览 | 新增/删除模块时更新 |
| L2 | `/{module}/CLAUDE.md` | 局部地图，成员清单与协作规则 | 文件夹结构变化时更新 |
| L3 | 文件头部注释 | INPUT/OUTPUT/POS 协议 | 文件逻辑变更时更新 |

### 强制回溯环

```
代码变更 → 更新 L3 头部注释 → 检查 L2 CLAUDE.md → 必要时更新 L1 CLAUDE.md
```

## 核心同步协议 (Mandatory)

1. **原子更新规则**: 任何功能、架构、写法更新，必须在代码修改完成后，[立即]同步更新对应目录的子文档。
2. **逆归触发**: 文件变更 -> 更新文件Header -> 更新所属文件夹CLAUDE.md -> (若影响全局) 更新主CLAUDE.md。
3. **分形自治**: 确保系统在任何一个子目录下，Claude都能通过该目录的CLAUDE.md重建局部世界观。

## L2 模板（文件夹级 CLAUDE.md）

每个文件夹必须包含一个 CLAUDE.md，格式如下：

```markdown
# {FolderName}/

> L2 文档 | 父级: [../CLAUDE.md](../CLAUDE.md) | 分形协议: 三层结构

1. **地位**: [该文件夹在系统中的角色]
2. **边界**: [输入输出边界定义]
3. **约束**: [必须遵守的规则]

## 成员清单

**filename.py**: [一句话描述功能和职责]

⚡触发器: 一旦本文件夹增删文件或架构逻辑调整，请立即重写此文档。
```

## L3 模板（文件头部注释）

每个 Python 文件开头必须包含：

```python
"""模块简述。

[INPUT]: 文件依赖外部的什么？
[OUTPUT]: 文件对外输出什么？
[POS]: 文件在当前L2中的定位是什么？

[PROTOCOL]:
1. 逻辑变更时同步更新此头部
2. 更新后检查所在文件夹的 CLAUDE.md
"""
```



## 项目概览

**awiki-skills** 是一个专为 Claude Code 设计的 AI 资讯聚合技能包，核心使命是**通过 MCP (Model Context Protocol) 协议连接远程服务，为用户实时聚合和提供 AI 领域的最新资讯和活动信息**。

主要功能包括：
- **📰 AI 日报摘要**：获取指定日期或最新的 AI 领域新闻日报汇总
- **🔍 活动搜索**：搜索 AI 相关的活动、会议、研讨会等事件

> **完整功能说明**: [README.md](README.md) | [awiki-info/SKILL.md](awiki-info/SKILL.md)

### 核心模块

| 模块 | 路径 | 职责 |
|------|------|------|
| **awiki-info** | [awiki-info/](awiki-info/) | AI 资讯聚合 Skill（MCP 客户端、日报获取、活动搜索） |

## 技术栈

- **Python**: 3.10+
- **包管理**: uv
- **MCP 框架**: MCP SDK 1.0+ (官方 Model Context Protocol 实现)
- **网络传输**: streamable-http (HTTP streaming 协议)
- **异步支持**: asyncio
- **HTTP 客户端**: httpx[socks]
- **CLI 框架**: argparse
- **测试框架**: pytest + pytest-asyncio

## 编程规范

1. 使用 Google Python 编程规范
2. 测试代码放到 tests/ 路径下
3. 正式代码中不要 mock
4. 永远用中文回答
5. **代码-测试同步**: 修改代码时，必须同步检查对应的测试用例是否需要更新
6. **AI 摘要验证**: 修改 AI 摘要相关提示词后，必须验证数据库中实际生成的摘要内容是否与提示词定义的格式一致（不能只看提示词本身，要检查 LLM 的实际输出）

## 快速命令

```bash
# 进入 awiki-info 目录
cd awiki-info

# 安装依赖
uv sync

# 获取 AI 日报
python scripts/get_daily_summary.py

# 获取指定日期的日报
python scripts/get_daily_summary.py --date 2026-01-27

# 搜索 AI 活动
python scripts/search_activities.py --keyword "LLM"

# 搜索未来 30 天的活动
python scripts/search_activities.py --future-days 30

# 运行测试
uv run pytest

# 发布新版本
python ../publish.py
```
