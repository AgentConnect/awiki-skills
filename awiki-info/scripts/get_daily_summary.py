#!/usr/bin/env python3
"""
获取 AI 日报摘要的命令行脚本
"""

import argparse
import asyncio
import json
import sys
from typing import Optional

from mcp_client import get_ai_daily_summary


def format_summary(data) -> str:
    """格式化日报输出"""
    output = []

    # 提取内容（处理 MCP 响应格式）
    if hasattr(data, "content") and data.content:
        # MCP CallToolResult 格式
        for content_item in data.content:
            if hasattr(content_item, "text"):
                try:
                    summary_data = json.loads(content_item.text)
                except json.JSONDecodeError:
                    output.append(content_item.text)
                    continue

                output.append(
                    f"# AI 日报 - {summary_data.get('summary_date', '未知日期')}"
                )
                output.append(f"\n**动态数量**: {summary_data.get('feed_count', 0)}")

                highlights = summary_data.get("highlights", {})
                if highlights.get("keywords"):
                    output.append(f"**关键词**: {', '.join(highlights['keywords'])}")

                output.append(f"\n{summary_data.get('content', '暂无内容')}")
    else:
        output.append(str(data))

    return "\n".join(output)


async def main(date: Optional[str] = None, server: Optional[str] = None) -> int:
    """主函数"""
    try:
        result = await get_ai_daily_summary(date=date, server_url=server)
        print(format_summary(result))
        return 0
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="获取 AI 日报摘要")
    parser.add_argument(
        "--date", type=str, help="日期，格式 YYYY-MM-DD，不传则获取最新"
    )
    parser.add_argument(
        "--server",
        type=str,
        help="MCP 服务器地址，默认 https://agent-connect.cn/protocol/mcp",
    )

    args = parser.parse_args()
    sys.exit(asyncio.run(main(date=args.date, server=args.server)))
