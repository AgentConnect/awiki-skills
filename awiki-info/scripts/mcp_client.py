#!/usr/bin/env python3
"""
MCP 客户端核心模块
使用 MCP Python SDK 通过 streamable-http 传输协议连接远程 MCP 服务器
"""

import os
from typing import Any, Optional

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

# 默认 MCP 服务器地址
DEFAULT_MCP_SERVER_URL = "https://agent-connect.cn/awiki/mcp"


class MCPClient:
    """MCP 客户端封装类"""

    def __init__(self, server_url: Optional[str] = None):
        """
        初始化 MCP 客户端

        Args:
            server_url: MCP 服务器地址，默认从环境变量或使用默认值
        """
        self.server_url = server_url or os.getenv(
            "AWIKI_MCP_SERVER_URL", DEFAULT_MCP_SERVER_URL
        )

    async def call_tool(
        self, tool_name: str, arguments: Optional[dict] = None
    ) -> Any:
        """
        调用 MCP 工具

        Args:
            tool_name: 工具名称
            arguments: 工具参数字典

        Returns:
            工具返回结果
        """
        async with streamable_http_client(self.server_url) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments or {})
                return result

    async def list_tools(self) -> list:
        """
        列出服务器可用的所有工具

        Returns:
            工具列表
        """
        async with streamable_http_client(self.server_url) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools = await session.list_tools()
                return tools.tools


async def get_ai_daily_summary(
    date: Optional[str] = None, server_url: Optional[str] = None
) -> Any:
    """
    获取 AI 日报摘要

    Args:
        date: 日期，格式 YYYY-MM-DD，不传则获取最新
        server_url: MCP 服务器地址

    Returns:
        日报摘要数据
    """
    client = MCPClient(server_url)
    arguments = {}
    if date:
        arguments["date"] = date
    return await client.call_tool("get_ai_daily_summary", arguments)


async def search_activities(
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    event_type: Optional[str] = None,
    start_time_min: Optional[int] = None,
    start_time_max: Optional[int] = None,
    start: int = 0,
    hits: int = 10,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
    server_url: Optional[str] = None,
) -> Any:
    """
    搜索活动/事件

    Args:
        keyword: 搜索关键词
        status: 活动状态 (draft/published/cancelled)
        event_type: 活动类型
        start_time_min: 开始时间最小值（Unix 时间戳）
        start_time_max: 开始时间最大值（Unix 时间戳）
        start: 分页起始位置
        hits: 返回数量 (1-100)
        sort_by: 排序字段或 RANK
        sort_order: 排序方向 (asc/desc)
        server_url: MCP 服务器地址

    Returns:
        搜索结果
    """
    client = MCPClient(server_url)

    arguments: dict[str, Any] = {
        "start": start,
        "hits": hits,
        "sort_order": sort_order,
    }

    if keyword:
        arguments["keyword"] = keyword
    if status:
        arguments["status"] = status
    if event_type:
        arguments["event_type"] = event_type
    if start_time_min is not None:
        arguments["start_time_min"] = start_time_min
    if start_time_max is not None:
        arguments["start_time_max"] = start_time_max
    if sort_by:
        arguments["sort_by"] = sort_by

    return await client.call_tool("search_activities", arguments)
