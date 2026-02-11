# awiki-skills 安装指南（面向 AI Agent）

本文档供 AI Agent 读取后自动完成 skill 安装。按顺序执行以下步骤即可。

- 仓库地址：https://github.com/AgentConnect/awiki-skills
- 当前可用 skill：`awiki-info`（AI 资讯聚合）

## 1. 前置条件检查

依次检查以下条件，任一不满足则按提示安装：

```bash
# 检查 Python 版本（需要 3.10+）
python3 --version

# 检查 uv 是否安装
uv --version
# 若未安装：curl -LsSf https://astral.sh/uv/install.sh | sh

# 确保 skills 目录存在
mkdir -p ~/.claude/skills
```

## 2. 下载 Skill 包

### 方案 A：使用 gh CLI（推荐）

```bash
# 检查 gh 是否可用
gh --version

# 下载最新 release 的 zip 包
gh release download --repo AgentConnect/awiki-skills --pattern "awiki-info-v*.zip" --dir /tmp
```

### 方案 B：使用 curl（备选）

```bash
# 获取最新版本号
LATEST_TAG=$(curl -sI https://github.com/AgentConnect/awiki-skills/releases/latest | grep -i '^location:' | sed 's|.*/||' | tr -d '\r')

# 下载 zip 包
curl -L -o /tmp/awiki-info-${LATEST_TAG}.zip \
  "https://github.com/AgentConnect/awiki-skills/releases/download/${LATEST_TAG}/awiki-info-${LATEST_TAG}.zip"
```

### 方案 C：从源码安装

```bash
git clone https://github.com/AgentConnect/awiki-skills.git /tmp/awiki-skills
cp -r /tmp/awiki-skills/awiki-info ~/.claude/skills/awiki-info
cp /tmp/awiki-skills/README.md ~/.claude/skills/awiki-info/README.md
cp /tmp/awiki-skills/LICENSE ~/.claude/skills/awiki-info/LICENSE
cp /tmp/awiki-skills/INSTALL.md ~/.claude/skills/awiki-info/INSTALL.md
rm -rf /tmp/awiki-skills
```

若使用方案 C，跳到第 4 步。

## 3. 解压安装

```bash
# 备份旧版本（如存在）
if [ -d ~/.claude/skills/awiki-info ]; then
  mv ~/.claude/skills/awiki-info ~/.claude/skills/awiki-info.bak.$(date +%Y%m%d%H%M%S)
fi

# 解压（zip 内的文件已在 awiki-info/ 目录下）
unzip -o /tmp/awiki-info-v*.zip -d ~/.claude/skills/

# 清理下载文件
rm -f /tmp/awiki-info-v*.zip
```

## 4. 安装依赖

```bash
cd ~/.claude/skills/awiki-info && uv sync
```

备选方式（无 uv 时）：

```bash
cd ~/.claude/skills/awiki-info && python3 install_dependencies.py
```

## 5. 验证安装

### 目录结构检查

确认以下文件存在：

```bash
ls ~/.claude/skills/awiki-info/SKILL.md
ls ~/.claude/skills/awiki-info/scripts/mcp_client.py
ls ~/.claude/skills/awiki-info/scripts/get_daily_summary.py
ls ~/.claude/skills/awiki-info/scripts/search_activities.py
```

### 依赖检查

```bash
cd ~/.claude/skills/awiki-info && uv run python -c "import mcp; print('mcp:', mcp.__version__)"
```

### 功能验证（可选）

```bash
cd ~/.claude/skills/awiki-info && uv run python scripts/get_daily_summary.py
```

若返回 AI 日报内容，说明安装成功。

## 6. 更新与卸载

### 更新

重复步骤 2-5 即可。旧版本会被自动备份。

### 卸载

```bash
rm -rf ~/.claude/skills/awiki-info
```

### 回滚

```bash
# 查看备份
ls ~/.claude/skills/ | grep awiki-info.bak

# 恢复指定备份
rm -rf ~/.claude/skills/awiki-info
mv ~/.claude/skills/awiki-info.bak.<时间戳> ~/.claude/skills/awiki-info
```

## 7. 常见错误处理

| 错误现象 | 原因 | 解决方案 |
|----------|------|----------|
| `uv: command not found` | 未安装 uv | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| `python3: No module named mcp` | 依赖未安装 | `cd ~/.claude/skills/awiki-info && uv sync` |
| `gh: command not found` | 未安装 gh CLI | 改用方案 B 或 C 下载 |
| `Connection error` | 网络问题或 MCP 服务不可达 | 检查网络；尝试 `curl https://agent-connect.cn/awiki/mcp` |
| `zip 解压后目录为空` | 下载不完整 | 重新下载，确认文件大小 > 0 |
| `Permission denied` | 目录权限不足 | `chmod -R u+rw ~/.claude/skills/awiki-info` |
