#!/usr/bin/env python3
"""
搜索 AI 活动的命令行脚本
"""

import argparse
import asyncio
import json
import sys
import time
from typing import Optional

from mcp_client import search_activities


def format_activities(data) -> str:
    """格式化活动搜索结果"""
    output = []

    # 提取内容（处理 MCP 响应格式）
    if hasattr(data, "content") and data.content:
        for content_item in data.content:
            if hasattr(content_item, "text"):
                try:
                    result = json.loads(content_item.text)
                except json.JSONDecodeError:
                    output.append(content_item.text)
                    continue

                total = result.get("total", 0)
                items = result.get("items", [])

                output.append("# AI 活动搜索结果\n")
                output.append(f"**匹配总数**: {total}\n")

                if not items:
                    output.append("暂无匹配的活动。")
                else:
                    for i, item in enumerate(items, 1):
                        output.append(f"## {i}. {item.get('title', '未知标题')}\n")
                        output.append(f"- **主办方**: {item.get('organizer', '未知')}")
                        output.append(f"- **地点**: {item.get('location', '未知')}")
                        output.append(f"- **时间**: {item.get('event_time', '未知')}")
                        output.append(f"- **状态**: {item.get('status', '未知')}")

                        if item.get("tags"):
                            output.append(f"- **标签**: {item['tags']}")
                        if item.get("source_url"):
                            output.append(f"- **详情**: {item['source_url']}")

                        details = item.get("details", {})
                        if details.get("description"):
                            desc = details["description"][:200]
                            if len(details["description"]) > 200:
                                desc += "..."
                            output.append(f"\n> {desc}")

                        output.append("")
    else:
        output.append(str(data))

    return "\n".join(output)


async def main(
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    event_type: Optional[str] = None,
    future_days: Optional[int] = None,
    hits: int = 10,
    start: int = 0,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
    server: Optional[str] = None,
) -> int:
    """主函数"""
    try:
        start_time_min = None
        start_time_max = None

        if future_days:
            start_time_min = int(time.time())
            start_time_max = start_time_min + (future_days * 24 * 3600)

        result = await search_activities(
            keyword=keyword,
            status=status,
            event_type=event_type,
            start_time_min=start_time_min,
            start_time_max=start_time_max,
            start=start,
            hits=hits,
            sort_by=sort_by,
            sort_order=sort_order,
            server_url=server,
        )

        print(format_activities(result))
        return 0
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="搜索 AI 活动")
    parser.add_argument("--keyword", type=str, help="搜索关键词")
    parser.add_argument(
        "--status",
        type=str,
        choices=["draft", "published", "cancelled"],
        help="活动状态",
    )
    parser.add_argument("--event-type", type=str, help="活动类型")
    parser.add_argument("--future-days", type=int, help="搜索未来 N 天内的活动")
    parser.add_argument("--hits", type=int, default=10, help="返回数量 (1-100)")
    parser.add_argument("--start", type=int, default=0, help="分页起始位置")
    parser.add_argument("--sort-by", type=str, help="排序字段 (start_time/RANK)")
    parser.add_argument(
        "--sort-order",
        type=str,
        default="desc",
        choices=["asc", "desc"],
        help="排序方向",
    )
    parser.add_argument("--server", type=str, help="MCP 服务器地址")

    args = parser.parse_args()
    sys.exit(
        asyncio.run(
            main(
                keyword=args.keyword,
                status=args.status,
                event_type=args.event_type,
                future_days=args.future_days,
                hits=args.hits,
                start=args.start,
                sort_by=args.sort_by,
                sort_order=args.sort_order,
                server=args.server,
            )
        )
    )
