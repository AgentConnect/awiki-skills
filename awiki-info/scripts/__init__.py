"""awiki-info MCP 客户端脚本包"""

from .mcp_client import (
    DEFAULT_MCP_SERVER_URL,
    MCPClient,
    get_ai_daily_summary,
    search_activities,
)

__all__ = [
    "DEFAULT_MCP_SERVER_URL",
    "MCPClient",
    "get_ai_daily_summary",
    "search_activities",
]
